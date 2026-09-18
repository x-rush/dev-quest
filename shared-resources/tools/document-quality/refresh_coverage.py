"""Refresh existing reviewed coverage against the current structural inventory.

Review status is recorded evidence, never inferred from keyword/fence checks.
New documents stay unreviewed until an editor records their status.
"""
import json
from collections import Counter
from pathlib import Path

REPORTS = Path(__file__).resolve().parent / 'reports'
inventory = json.loads((REPORTS / 'after.json').read_text(encoding='utf8'))
previous = json.loads((REPORTS / 'coverage.json').read_text(encoding='utf8'))
by_path = {row['path']: row for row in previous['documents']}
rows = []
for doc in inventory['documents']:
    if not doc['active']:
        continue
    row = dict(by_path.get(doc['path'], {'path': doc['path'], 'status': '新增文档，教学内容待审查', 'editorial_sections': 0, 'editorial_detail': ''}))
    row['structure_signals'] = doc['signals']
    rows.append(row)
counts = dict(Counter(row['status'] for row in rows))
(REPORTS / 'coverage.json').write_text(json.dumps({'counts': counts, 'documents': rows}, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
text = '# 逐文件增强台账\n\n教学内容处理与运行验证分别记录。正文增强不等于每个历史断言已核验；结构线索既不是自动判错，也不是合格分数。\n\n'
text += '| 处理层级 | 文档数 |\n|---|---:|\n' + ''.join(f'| {key} | {value} |\n' for key, value in counts.items())
for module in sorted({row['path'].split('/')[0] for row in rows}):
    text += f'\n## {module}\n\n| 文档 | 本轮处理 | 结构复核线索 |\n|---|---|---|\n'
    for row in rows:
        if row['path'].split('/')[0] == module:
            text += f'| [{row["path"].split("/",1)[1]}](../../../../{row["path"]}) | {row["status"]}{row["editorial_detail"]} | {"；".join(row["structure_signals"]) or "未命中；不代表技术验证通过"} |\n'
(REPORTS / 'coverage.md').write_text(text,encoding='utf8')
print(json.dumps(counts,ensure_ascii=False,indent=2))
