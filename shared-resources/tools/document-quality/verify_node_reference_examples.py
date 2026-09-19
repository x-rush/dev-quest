"""Execute only the selected complete JavaScript examples added in the editorial pass."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
PREFIX = '09-nodejs-backend/reference/'
CASES = [
    ('language-concepts/01-js-modern-syntax.md', 'modern-syntax: fallback=3/0/null; shared=node,js\n'),
    ('language-concepts/03-node-core-api.md', 'start\nemit returned\nafter await\n'),
    ('language-concepts/07-js-core-semantics.md', '2\n0,1,2\n'),
    ('language-concepts/08-type-coercion-collections.md', '0 0 true\nfalse 2\n{"empty":null}\n'),
    ('library-guides/04-child-process.md', 'a b; c\n'),
    ('library-guides/05-buffer.md', 'shared=1,9,3,4 copy=2,3,4\ntrailer=772\nshort=trailer needs two bytes\n'),
    ('library-guides/08-test-runner.md', None),
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', default='node')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    results = []
    with tempfile.TemporaryDirectory(prefix='dev-quest-node-') as tmp:
        for index, (relative, expected) in enumerate(CASES):
            path = PREFIX + relative
            text = (ROOT / path).read_text(encoding='utf8').split('<!-- full-library-explanation -->', 1)[1]
            code = re.findall(r'```js\s*\n(.*?)\n```', text, re.S)[0]
            file = Path(tmp) / f'example-{index}.mjs'
            file.write_text(code, encoding='utf8')
            command = [args.node, str(file)] if expected is not None else [args.node, '--test', '--test-reporter=tap', str(file)]
            process = subprocess.run(command, capture_output=True, text=True, encoding='utf8', timeout=30)
            output = process.stdout.replace('\r\n', '\n')
            if process.returncode or (expected is not None and output != expected):
                raise AssertionError({'path': path, 'output': output, 'stderr': process.stderr, 'expected': expected})
            if expected is None and ('# pass 1' not in output or '# fail 0' not in output):
                raise AssertionError(output)
            results.append({'source': path, 'status': 'PASS', 'output': output})
    version = subprocess.check_output([args.node, '--version'], text=True).strip()
    report = {'node': version, 'results': results, 'scope': 'Seven selected complete added examples only. Frameworks, databases, clusters, deployment and historical snippets are not executed by this check.'}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'examples': len(results), 'status': 'PASS', 'node': version}))

if __name__ == '__main__':
    main()
