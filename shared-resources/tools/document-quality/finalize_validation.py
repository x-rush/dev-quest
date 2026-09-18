"""Recheck structure/links/anchors/whitespace; aggregate retained scoped runs."""
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
REPORTS=Path(__file__).resolve().parent/'reports'
results={}
commands={
    'structure':[sys.executable,'shared-resources/tools/document-quality/audit.py','--output','shared-resources/tools/document-quality/reports/after.json'],
    'relative_links':[sys.executable,'shared-resources/tools/code-block-verify/link_check.py','.','--strict'],
    'anchors':[sys.executable,'shared-resources/tools/document-quality/check_anchors.py','--report','shared-resources/tools/document-quality/reports/anchors.json'],
    'diff_whitespace':['git','-c','core.safecrlf=false','diff','--check'],
}
for label,command in commands.items():
    process=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf8',timeout=45)
    results[label]={'exit_code':process.returncode,'stdout':process.stdout.strip(),'stderr':process.stderr.strip()}
    if process.returncode:raise RuntimeError(results[label])
after=json.loads((REPORTS/'after.json').read_text(encoding='utf8'))
unclosed=[row['path'] for row in after['documents'] if '未闭合代码围栏' in row['signals']]
assert not unclosed,unclosed
results['fences']={'documents':after['summary']['documents'],'unclosed':unclosed}
results['retained_example_runs']={name:json.loads((REPORTS/name).read_text(encoding='utf8')) for name in [
    'examples.json','reference-examples.json','node-reference-examples.json','go-reference-examples.json','final-web-examples.json']}
old=json.loads((REPORTS/'validation.json').read_text(encoding='utf8'))
for key in ['query_ui','typescript','environment']:
    if key in old:results[key]=old[key]
results['verification_basis']={
    'rerun_here':list(commands)+['fences'],
    'retained_previous_runs':'Example reports preserve their original scope; this aggregation does not re-execute those examples.',
    'web_final':'Seven checks cover extracted LRU, Query hydration, URL input normalization, strict typing and DataFetcher stale-response/error/unmount behavior.',
    'go':'13 selected programs passed earlier; 2 blocked by Windows application control. No bypass or full project/race/database execution claimed.',
}
results['not_executed']=['Java/Spring full projects','Rust compilation','PHP compilation/runtime','Android/Compose toolchain and devices','Swift/SwiftUI SDK and devices','all historical code blocks','full application builds/deployments','all external URLs','renderer-based visual/anchor validation']
(REPORTS/'validation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({key:results[key]['stdout'] for key in ['relative_links','anchors','diff_whitespace']},ensure_ascii=False,indent=2))
