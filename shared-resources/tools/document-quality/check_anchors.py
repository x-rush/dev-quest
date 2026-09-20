"""Check local Markdown fragments using GitHub-style heading slugs.

Static heading/HTML-id check only; no browser rendering or external URL validation.
"""
import argparse
import html
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]

def prose(text):
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if match:
            mark, rest = match.groups()
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence) and not rest.strip():
                fence = None
            continue
        if fence is None:
            yield number, line

def slug(text):
    # Inline code such as Box<dyn Trait> is text, not an HTML tag.
    text = re.sub(r'`([^`]+)`', lambda m: html.escape(m.group(1)), text)
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'!?\[([^\]]+)\]\([^)]*\)', r'\1', text)
    text = html.unescape(text).lower().strip()
    # Keep letters, marks, numbers, spaces, underscore and hyphen.
    return ''.join(c for c in text if c in ' _-' or unicodedata.category(c)[0] in 'LMN').replace(' ', '-')

def anchors(path):
    found, counts = set(), {}
    for _, line in prose(path.read_text(encoding='utf8')):
        found.update(re.findall(r'<a\s+(?:name|id)=["\']([^"\']+)', line))
        match = re.match(r'^ {0,3}#{1,6}\s+(.+?)\s*#*$', line)
        if match:
            base = slug(match.group(1))
            index = counts.get(base, 0)
            counts[base] = index + 1
            found.add(base if index == 0 else f'{base}-{index}')
    return found

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    cache, issues, checked = {}, [], 0
    for path in ROOT.rglob('*.md'):
        if any(p in {'.git','node_modules','reports'} for p in path.relative_to(ROOT).parts):
            continue
        for number,line in prose(path.read_text(encoding='utf8')):
            for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)',line):
                if '#' not in target or re.match(r'^[a-zA-Z][\w+.-]*:',target):
                    continue
                file, fragment = target.strip('<>').split('#',1)
                if not fragment: continue
                dest = (path.parent / unquote(file)).resolve() if file else path
                if not dest.is_file() or dest.suffix != '.md': continue
                checked += 1
                if dest not in cache: cache[dest] = anchors(dest)
                if unquote(fragment) not in cache[dest]:
                    issues.append({'source':path.relative_to(ROOT).as_posix(),'line':number,'target':target})
    result={'checked':checked,'issues':issues,'scope':'Active and shared Markdown; static GitHub-style headings and explicit a ids. Archives/reports and external URLs excluded.'}
    args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'checked':checked,'issues':len(issues)},ensure_ascii=False))
    return bool(issues)

if __name__ == '__main__':
    raise SystemExit(main())
