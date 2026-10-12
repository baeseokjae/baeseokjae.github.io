"""Validate the same pinned Hugo binary, theme and options locally and in CI."""
import argparse
import hashlib
import json
import platform
import re
import shutil
import subprocess
from pathlib import Path


def command(args, root):
    return subprocess.check_output(args, cwd=root, text=True, stderr=subprocess.PIPE).strip()


def verify(root):
    root = Path(root)
    raw = (root/'.hugo-build.json').read_bytes(); config = json.loads(raw)
    if config.get('version') != 1 or config.get('flags') != ['--minify','--buildFuture','--environment','production']:
        raise ValueError('Unsupported build contract')
    if hashlib.sha256((root/'hugo.toml').read_bytes()).hexdigest() != config.get('config_sha256'):
        raise ValueError('Site configuration differs from reviewed build contract')
    binary = shutil.which('hugo')
    if not binary: raise ValueError('Hugo executable missing')
    arch = {'aarch64':'arm64','arm64':'arm64','x86_64':'amd64','AMD64':'amd64'}.get(platform.machine())
    digest = hashlib.sha256(Path(binary).read_bytes()).hexdigest()
    expected = config.get('binary_sha256',{}).get(arch)
    if not expected or digest != expected: raise ValueError('Hugo binary differs from verified official release')
    version = command([binary,'version'],root)
    if not re.search(r'\bv'+re.escape(config['hugo_version'])+r'(?:-|\+|\s)',version) or '+extended' not in version:
        raise ValueError('Hugo version/edition differs from contract')
    tracked = command(['git','ls-tree','HEAD','themes/PaperMod'],root).split()[2]
    actual = command(['git','rev-parse','HEAD'],root/'themes/PaperMod')
    if tracked != config['theme_commit'] or actual != tracked:
        raise ValueError('Theme differs from pinned source commit')
    if command(['git','status','--porcelain','--untracked-files=all'],root/'themes/PaperMod'):
        raise ValueError('Theme contains unreviewed changes')
    return {'hugo_version':config['hugo_version'],'theme_commit':actual,'flags':config['flags'],
            'config_sha256':config['config_sha256'],
            'contract_sha256':hashlib.sha256(raw).hexdigest(), 'binary_sha256':digest,'architecture':arch}


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--build',action='store_true');parser.add_argument('--output',type=Path)
    args=parser.parse_args();proof=verify(args.root)
    if args.build:
        subprocess.run(['hugo',*proof['flags']],cwd=args.root,check=True)
        if verify(args.root)!=proof:raise SystemExit('Build contract changed during generation')
    text=json.dumps(proof,indent=2)
    if args.output:args.output.write_text(text+'\n')
    print(text)
