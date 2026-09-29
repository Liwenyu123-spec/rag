# -*- coding: utf-8 -*-
import ast

p = r"h:\Python工程\rag\chroma文档管理\semantic_search\app\service\rag_service.py"
src = open(p, encoding="utf-8").read()
ast.parse(src)
lines = src.splitlines()
print("total_lines", len(lines))
missing = []
for i, l in enumerate(lines, 1):
    s = l.strip()
    if not s:
        continue
    if s.startswith("#"):
        continue
    if "#" not in l:
        missing.append((i, l[:120]))
print("missing_count", len(missing))
for m in missing:
    print(m[0], m[1])
