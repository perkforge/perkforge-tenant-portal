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
        prefix = "example.perkforge.io/"
        self.assertEqual(context[prefix + "cluster"], cluster)
        self.assertIn("../../environments/" + context[prefix + "environment"], root["resources"])
        self.assertIn("../../profiles/" + context[prefix + "profile"], root["resources"])

    def render(self, objects, enabled=False, digest=True):
        release = next(obj for obj in objects if obj["kind"] == "HelmRelease")
        maps = {obj["metadata"]["name"]: obj for obj in objects
                if obj["kind"] == "ConfigMap"}
        with tempfile.TemporaryDirectory() as directory:
            args = ["helm", "template", "portal", str(ROOT / "bundles/portal/chart")]
            for index, ref in enumerate(release["spec"]["valuesFrom"]):
                path = Path(directory) / f"values-{index}.yaml"
                path.write_text(maps[ref["name"]]["data"][ref["valuesKey"]])
                args += ["-f", str(path)]
            if enabled:
                args += ["--set", "enabled=true"]
                if digest:
                    args += ["--set-string", "image.digest=sha256:" + "a" * 64]
            output = subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)
        return [obj for obj in yaml.safe_load_all(output) if obj]

    def test_roots_remain_app_only_suspended_and_disabled(self):
        for cluster in ("local", "dev-il2", "dev-il5"):
            with self.subTest(cluster=cluster):
                objects = self.build(cluster)
                self.assertEqual({obj["kind"] for obj in objects},
                                 {"ConfigMap", "HelmRelease"})
                release = next(obj for obj in objects if obj["kind"] == "HelmRelease")
                self.assertTrue(release["spec"]["suspend"])
                self.assertEqual(release["spec"]["serviceAccountName"], "portal-deployer")
                self.assertEqual(release["spec"]["chart"]["spec"]["sourceRef"]["name"],
                                 "tenant-portal")
                self.assertEqual([ref["name"] for ref in release["spec"]["valuesFrom"]],
                                 ["portal-defaults", "portal-environment", "portal-profile", "portal-cluster"])
                self.assertEqual(self.render(objects), [])

    def test_two_dev_clusters_share_environment_with_last_cluster_override(self):
        origins = {"dev-il2": "https://portal.dev-il2.example.invalid",
                   "dev-il5": "https://portal.dev-il5.example.invalid"}
        for cluster, origin in origins.items():
            with self.subTest(cluster=cluster):
                objects = self.render(self.build(cluster), enabled=True)
                self.assertEqual({obj["kind"] for obj in objects}, {"Deployment", "Service"})
                pod = next(obj for obj in objects if obj["kind"] == "Deployment")["spec"]["template"]["spec"]
                env = {item["name"]: item for item in pod["containers"][0]["env"]}
                self.assertEqual(env["PORTAL_ORIGIN"]["value"], origin)
                self.assertEqual(env["OIDC_ISSUER"]["value"],
                                 "https://identity.dev.example.invalid")
                self.assertEqual(env["OIDC_CLIENT_ID"]["value"], "example-dev-client")
                self.assertEqual(env["OIDC_AUDIENCE"]["value"],
                                 "example-portal-" + ("il2" if cluster == "dev-il2" else "il5"))
                self.assertEqual(env["OIDC_CLIENT_SECRET"]["valueFrom"]["secretKeyRef"]["name"],
                                 "portal-oidc-existing")
                self.assertEqual(pod["serviceAccountName"], "portal-runtime")
                self.assertFalse(pod["automountServiceAccountToken"])

    def test_new_cluster_reuses_dev_without_copying_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            tree = Path(directory) / "gitops"
            shutil.copytree(ROOT / "gitops", tree)
            shutil.copytree(tree / "clusters/dev-il5", tree / "clusters/team-dev")
            selection = tree / "clusters/team-dev/kustomization.yaml"
            data = yaml.safe_load(selection.read_text())
            data["commonAnnotations"]["example.perkforge.io/cluster"] = "team-dev"
            selection.write_text(yaml.safe_dump(data, sort_keys=False))
            (tree / "clusters/team-dev/values.yaml").write_text(
                "portalOrigin: https://portal.team-dev.example.invalid\n")
            objects = self.render(self.build("team-dev", tree), enabled=True)
            pod = next(obj for obj in objects if obj["kind"] == "Deployment")["spec"]["template"]["spec"]
            env = {item["name"]: item for item in pod["containers"][0]["env"]}
            self.assertEqual(env["PORTAL_ORIGIN"]["value"],
                             "https://portal.team-dev.example.invalid")
            self.assertEqual(env["OIDC_ISSUER"]["value"],
                             "https://identity.dev.example.invalid")

    def test_enablement_without_an_approved_digest_fails_closed(self):
        with self.assertRaises(subprocess.CalledProcessError) as error:
            self.render(self.build("dev-il2"), enabled=True, digest=False)
        self.assertIn("immutable image digest", error.exception.output)

    def test_mismatched_environment_profile_or_cluster_is_rejected(self):
        for kind, wrong in (("environment", "local"), ("profile", "il5"), ("cluster", "other-dev")):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                tree = Path(directory) / "gitops"
                shutil.copytree(ROOT / "gitops", tree)
                selection = tree / "clusters/dev-il2/kustomization.yaml"
                root = yaml.safe_load(selection.read_text())
                root["commonAnnotations"]["example.perkforge.io/" + kind] = wrong
                selection.write_text(yaml.safe_dump(root, sort_keys=False))
                with self.assertRaises(AssertionError):
                    self.build("dev-il2", tree)
