"""Offline contract checks for app-only Flux cluster/environment composition."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


class FluxLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for tool in ("helm", "kubectl"):
            if not shutil.which(tool):
                raise RuntimeError(f"Offline tests require existing {tool} on PATH")

    def build(self, cluster, tree=None):
        path = (tree or ROOT / "gitops") / "clusters" / cluster
        self.check_selection(path, cluster)
        output = subprocess.check_output(
            ["kubectl", "kustomize", str(path)], text=True,
            env={**os.environ, "KUBECONFIG": "/dev/null"},
        )
        return [obj for obj in yaml.safe_load_all(output) if obj]

    def check_selection(self, path, cluster):
        root = yaml.safe_load((path / "kustomization.yaml").read_text())
        context = root["commonAnnotations"]
        prefix = "platform.perkforge.io/"
        self.assertEqual(context[prefix + "cluster"], cluster)
        self.assertIn("../../environments/" + context[prefix + "environment"], root["resources"])
        self.assertIn("../../profiles/" + context[prefix + "profile"], root["resources"])

    def render(self, objects, enabled=False, digest=True):
        release = next(obj for obj in objects if obj["kind"] == "HelmRelease")
        maps = {obj["metadata"]["name"]: obj for obj in objects
                if obj["kind"] == "ConfigMap"}
        with tempfile.TemporaryDirectory() as directory:
            args = ["helm", "template", "portal", str(ROOT / "bundles/portal/chart"),
                    "--namespace", release['spec'].get('targetNamespace', 'default')]
            for index, ref in enumerate(release["spec"]["valuesFrom"]):
                path = Path(directory) / f"values-{index}.yaml"
                path.write_text(maps[ref["name"]]["data"][ref["valuesKey"]])
                args += ["-f", str(path)]
            if enabled:
                args += ["--set", "enabled=true"]
                if digest:
                    args += ["--set-string", "image.digest=sha256:" + "a" * 64]
                else:
                    # Test missing-digest rejection even after local pins a real image.
                    args += ["--set-string", "image.digest="]
            output = subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)
        return [obj for obj in yaml.safe_load_all(output) if obj]

    def test_only_local_is_active_and_roots_remain_app_only(self):
        for cluster in ("local", "dev"):
            with self.subTest(cluster=cluster):
                objects = self.build(cluster)
                self.assertEqual({obj["kind"] for obj in objects},
                                 {"ConfigMap", "HelmRelease"})
                release = next(obj for obj in objects if obj["kind"] == "HelmRelease")
                self.assertEqual(release["spec"]["suspend"], cluster != "local")
                self.assertEqual(release["spec"]["serviceAccountName"], "portal-deployer")
                self.assertEqual(release["spec"]["chart"]["spec"]["sourceRef"]["name"],
                                 "tenant-portal")
                self.assertEqual([ref["name"] for ref in release["spec"]["valuesFrom"]],
                                 ["portal-defaults", "portal-environment", "portal-profile", "portal-cluster"])
                if cluster == 'local':
                    rendered = self.render(objects)
                    self.assertEqual({o['kind'] for o in rendered}, {'Deployment', 'Service'})
                    deployment = next(o for o in rendered if o['kind'] == 'Deployment')
                    self.assertEqual(deployment['spec']['template']['spec']['containers'][0]['image'],
                        'ghcr.io/perkforge/perkforge-portal@sha256:ae13143108562e9753eab40650cfcef4b53d8336e733adc6a94dbccabc0a2616')
                else:
                    self.assertEqual(self.render(objects), [])

    def test_shared_and_dev_safety_defaults_are_preserved(self):
        self.assertFalse(yaml.safe_load((ROOT/'gitops/shared/values.yaml').read_text())['enabled'])
        self.assertTrue(yaml.safe_load((ROOT/'gitops/shared/release.yaml').read_text())['spec']['suspend'])
        self.assertFalse(yaml.safe_load((ROOT/'bundles/portal/chart/values.yaml').read_text())['enabled'])
        self.assertEqual(self.render(self.build('dev')), [])
        self.assertEqual(yaml.safe_load((ROOT/'bundles/portal/chart/values.yaml').read_text())['accessPolicy'], 'home')

    def test_cluster_hosts_and_identity_follow_ordered_values(self):
        for cluster in ("local", "dev"):
            with self.subTest(cluster=cluster):
                objects = self.render(self.build(cluster), enabled=True)
                self.assertEqual({obj["kind"] for obj in objects}, {"Deployment", "Service"})
                pod = next(obj for obj in objects if obj["kind"] == "Deployment")["spec"]["template"]["spec"]
                env = {item["name"]: item for item in pod["containers"][0]["env"]}
                self.assertEqual(env["PORTAL_ORIGIN"]["value"],
                                 f"https://portal-{cluster}-il2.local-lab.test")
                self.assertEqual(env["OIDC_ISSUER"]["value"],
                                 'https://keycloak-local-il2.local-lab.test/auth/realms/perkforge'
                                 if cluster == 'local' else 'https://keycloak-dev-il2.local-lab.test/realms/household')
                self.assertEqual(env["OIDC_CLIENT_ID"]["value"], 'portal-local' if cluster == 'local' else 'example-dev-client')
                self.assertEqual(env["OIDC_AUDIENCE"]["value"], 'portal-local' if cluster == 'local' else 'example-portal-il2')
                self.assertEqual(env['PORTAL_ACCESS_POLICY']['value'], 'platform-admins' if cluster == 'local' else 'home')
                self.assertEqual(env["OIDC_CLIENT_SECRET"]["valueFrom"]["secretKeyRef"]["name"],
                                 "portal-oidc-existing")
                self.assertEqual(pod["serviceAccountName"], "portal-runtime")
                self.assertFalse(pod["automountServiceAccountToken"])
                if cluster == 'local':
                    release = next(o for o in self.build(cluster) if o['kind'] == 'HelmRelease')
                    self.assertEqual(release['spec']['targetNamespace'], 'tenant-portal')
                    self.assertEqual(release['spec']['storageNamespace'], 'tenant-portal-release')
                    self.assertEqual(next(o for o in objects if o['kind']=='Deployment')['metadata']['namespace'], 'tenant-portal')
                    self.assertEqual(pod['imagePullSecrets'], [{'name':'portal-registry-existing'}])
                    self.assertEqual(pod['nodeSelector'], {'kubernetes.io/hostname':'cks-worker'})
                    self.assertEqual(env['NODE_EXTRA_CA_CERTS']['value'], '/etc/portal/identity-ca/ca.crt')
                    self.assertEqual(pod['hostAliases'][0]['hostnames'], ['keycloak-local-il2.local-lab.test'])

    def test_new_cluster_reuses_dev_without_copying_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            tree = Path(directory) / "gitops"
            shutil.copytree(ROOT / "gitops", tree)
            shutil.copytree(tree / "clusters/dev", tree / "clusters/team-dev")
            selection = tree / "clusters/team-dev/kustomization.yaml"
            data = yaml.safe_load(selection.read_text())
            data["commonAnnotations"]["platform.perkforge.io/cluster"] = "team-dev"
            selection.write_text(yaml.safe_dump(data, sort_keys=False))
            (tree / "clusters/team-dev/values.yaml").write_text(
                "portalOrigin: https://portal-team-dev-il2.local-lab.test\n"
                "identity:\n  issuer: https://keycloak-dev-il2.local-lab.test/realms/household\n")
            objects = self.render(self.build("team-dev", tree), enabled=True)
            pod = next(obj for obj in objects if obj["kind"] == "Deployment")["spec"]["template"]["spec"]
            env = {item["name"]: item for item in pod["containers"][0]["env"]}
            self.assertEqual(env["PORTAL_ORIGIN"]["value"],
                             "https://portal-team-dev-il2.local-lab.test")
            self.assertEqual(env["OIDC_ISSUER"]["value"],
                             "https://keycloak-dev-il2.local-lab.test/realms/household")

    def test_enablement_without_an_approved_digest_fails_closed(self):
        with self.assertRaises(subprocess.CalledProcessError) as error:
            self.render(self.build("dev"), enabled=True, digest=False)
        self.assertIn("immutable image digest", error.exception.output)

    def test_mismatched_environment_profile_or_cluster_is_rejected(self):
        for kind, wrong in (("environment", "local"), ("profile", "unselected-profile"), ("cluster", "other-dev")):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                tree = Path(directory) / "gitops"
                shutil.copytree(ROOT / "gitops", tree)
                selection = tree / "clusters/dev/kustomization.yaml"
                root = yaml.safe_load(selection.read_text())
                root["commonAnnotations"]["platform.perkforge.io/" + kind] = wrong
                selection.write_text(yaml.safe_dump(root, sort_keys=False))
                with self.assertRaises(AssertionError):
                    self.build("dev", tree)
