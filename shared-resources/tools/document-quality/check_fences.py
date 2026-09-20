"""Fast deterministic Markdown fence check (no code execution)."""
from pathlib import Path
import json
import re
import sys
ROOT = Path(__file__).resolve().parents[3]

def unclosed(text):
    opened = None
    for n,line in enumerate(text.splitlines(), 1):
        m = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if not m: continue
        marker, tail = m.groups()
        if opened is None:
            opened = (marker[0],len(marker),n)
        elif marker[0] == opened[0] and len(marker) >= opened[1] and not tail.strip():
            opened = None
    return opened[2] if opened else None

if __name__ == '__main__':
    issues=[]
    for path in ROOT.rglob('*.md'):
        if set(path.relative_to(ROOT).parts) & {'.git','node_modules','reports'}: continue
        line = unclosed(path.read_text(encoding='utf8'))
        if line: issues.append({'file':path.relative_to(ROOT).as_posix(),'line':line})
    print(json.dumps({'unclosed_fences':issues},ensure_ascii=False,indent=2))
    sys.exit(bool(issues))
