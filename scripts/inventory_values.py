"""Materialize/verify inventory values from a published exact Git source, never hand-copy."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]
REPO = 'perkforge/perkforge-platform-tenants'
SELECTORS = ('local', 'dev', 'local-nextcloud', 'local-nextcloud-portal')


def values(content, commit, tag, selector):
    if not re.fullmatch(r'[a-f0-9]{40}', commit) or not re.fullmatch(r'v\d+\.\d+\.\d+', tag) or selector not in SELECTORS or len(content) > 131072:
        raise ValueError('Invalid immutable enrollment input')
    data = json.loads(content)
    if data.get('schemaVersion') != 1 or data.get('evidenceType') != 'declared-enrollment-selection' or not isinstance(data.get('selections', {}).get(selector), list):
        raise ValueError('Unsupported inventory')
    return {'enrollmentInventory': {'enabled': True, 'sourceCommit': commit, 'sourceTag': tag,
            'selector': selector, 'sha256': hashlib.sha256(content).hexdigest(), 'content': content.decode('utf-8')}}


def verify_remote():
    for path in sorted((ROOT/'gitops/clusters').glob('*/enrollment-inventory.values.yaml')):
        actual = yaml.safe_load(path.read_text())
        item = actual['enrollmentInventory']
        # Validate before constructing subprocess parameters; no shell interpolation.
        expected = values(item['content'].encode(), item['sourceCommit'], item['sourceTag'], item['selector'])
        subprocess.run([str(ROOT/'scripts/verify-release-ref.sh'), REPO, item['sourceTag'], item['sourceCommit']], check=True)
        content = subprocess.check_output(['gh', 'api', f'repos/{REPO}/contents/enrollment-inventory.json?ref={item["sourceCommit"]}', '-H', 'Accept: application/vnd.github.raw+json'])
        if actual != expected or actual != values(content, item['sourceCommit'], item['sourceTag'], item['selector']):
            raise ValueError(f'Stale or altered inventory values: {path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-remote', action='store_true')
    parser.add_argument('--checkout', type=Path)
    parser.add_argument('--tag')
    parser.add_argument('--selector', choices=SELECTORS)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.verify_remote:
        verify_remote()
    else:
        if not args.checkout or not args.output or not args.tag or not re.fullmatch(r'v\d+\.\d+\.\d+', args.tag):
            parser.error('checkout, release tag, selector and output required')
        commit = subprocess.check_output(['git','-C',str(args.checkout),'rev-parse',args.tag+'^{commit}'],text=True).strip()
        content = subprocess.check_output(['git','-C',str(args.checkout),'show',commit+':enrollment-inventory.json'])
        args.output.write_text(yaml.safe_dump(values(content, commit, args.tag, args.selector),sort_keys=False))
