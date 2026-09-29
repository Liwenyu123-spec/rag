import pathlib

root = pathlib.Path(r"h:/Python工程/rag/chroma文档管理/semantic_search")
files = [
    f
    for f in root.rglob("*.py")
    if "chroma_db" not in str(f) and "__pycache__" not in str(f)
]
for f in sorted(files):
    missing = 0
    codeish = 0
    for ln in f.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith('"""') or s.startswith("'''"):
            continue
        codeish += 1
        if "#" not in ln:
            missing += 1
    print(f"{missing:4d}/{codeish:4d} missing | {f.relative_to(root)}")
