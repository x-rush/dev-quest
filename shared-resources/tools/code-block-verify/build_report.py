"""Human-readable inventory; never silently equate a skipped check with PASS."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys


def classify(record):
    statuses = {s['status'] for s in (record['l1'], record['l2']) if s}
    if statuses & {'FAIL', 'ERROR_TOOL', 'MISS', 'TIMEOUT'}:
        return 'NEEDS_REVIEW'
    if record['l1']['status'] == 'PASS':
        return 'PASS_CHECKED_SCOPE'
    return 'NOT_VERIFIED'


def build_report(blocks, results, directory, commands, tools, execute):
    directory = Path(directory)
    versions = {'python': sys.version, 'platform': platform.platform()}
    for name, command in {'go': ['go','version'], 'node': ['node','--version'],
            'typescript': ['tsc','--version'], 'php': ['php','--version'],
            'java': ['java','-version'], 'rust': ['rustc','--version'],
            'swift': ['swiftc','--version'], 'kotlin': ['kotlinc','-version'],
            'protobuf': ['protoc','--version']}.items():
        if not shutil.which(command[0]):
            versions[name] = 'not installed'
            continue
        try:
            p = subprocess.run(command, capture_output=True, text=True, timeout=20)
            versions[name] = p.stdout + p.stderr
        except (OSError, subprocess.TimeoutExpired) as e:
            versions[name] = str(e)
    legacy = {json.loads(line)['hash'] for line in
              (directory/'adjudicated-fails.jsonl').read_text().splitlines() if line}
    rows = []
    for b in blocks:
        r = results[b['id']]
        r['classification'] = classify(r)
        r['source_sha256'] = hashlib.sha256(b.get('content','').encode()).hexdigest()
        r['legacy_hash_exception'] = b.get('hash') in legacy
        # Link individual commands where the generated block file is in args;
        # batch commands and in-process parsers are documented in the runner map.
        r['command_log_indices'] = [i for i,c in enumerate(commands)
            if re.search(r'\bb'+re.escape(b['id'])+r'\.', ' '.join(c['command']))]
        rows.append(r)
    counts = dict(Counter(r['classification'] for r in rows))
    summary = {'counts': counts, 'total':len(rows), 'execution_enabled':execute,
               'tools':{k:bool(v) for k,v in tools.items()}, 'versions':versions,
               'scope':'PASS_CHECKED_SCOPE is only the checks listed in l1/l2. No framework integration guarantee.',
               'commands':'commands.jsonl contains complete stdout/stderr and exact invocations. Python AST/data parsers run in-process; Go/TS use batches.',
               'legacy':'Existing hash-only exceptions lack per-item rationale. They remain visible; no new exception is created by this report.'}
    (directory/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    lines=['# Code block verification report','',f'Total: {len(rows)}. Execution enabled: {execute}.', '',
           'Status counts: `'+json.dumps(counts)+'`','',
           'PASS means only the recorded check passed. NOT_VERIFIED and skipped runtime checks are not success. Old hash exceptions are not a reviewed teaching classification.', '',
           '| Source | Block | L1 | L2 | Classification | Legacy exception |',
           '|---|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['file']}:{r['start']} | {r['id']} | {r['l1']['status']} | {r['l2']['status']} | {r['classification']} | {r['legacy_hash_exception']} |")
    lines += ['', '## All actionable diagnostics', '']
    for r in rows:
        if r['classification'] != 'NEEDS_REVIEW': continue
        lines += [f"### {r['file']}:{r['start']} (block {r['id']})",'']
        for level in ('l1','l2'):
            if r[level]['status'] in {'FAIL','ERROR_TOOL','MISS','TIMEOUT'}:
                lines += [level+': '+r[level]['status'], '', '    '+r[level].get('detail','').replace('\n','\n    '),'']
    (directory/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
