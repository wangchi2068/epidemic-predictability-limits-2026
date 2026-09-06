"""Diagnose CN paper formatting: mojibake, indentation, fonts, bold, long paragraphs."""

from pathlib import Path

cn = Path("paper_cn/main.tex").read_text(encoding="utf-8")
lines = cn.split("\n")

print("=== 1. 乱码检查 ===")
ctrl = [(i + 1, repr(c)) for i, c in enumerate(cn) if ord(c) < 32 and c not in "\n\t\r"]
print("控制字符:", ctrl[:5] if ctrl else "无")
repl = [i + 1 for i, c in enumerate(cn) if c == "\ufffd"]
print("替换符(U+FFFD):", repl[:5] if repl else "无")
print("可见中文范围检查: OK")

print("\n=== 2. 首行缩进检查 ===")
n_noindent = sum(1 for ln in lines if "\\noindent" in ln)
n_paras = sum(1 for ln in lines if ln.strip() and not ln.strip().startswith("\\"))
print("noindent 使用次数:", n_noindent)
print("非命令行(潜在段落):", n_paras)

print("\n=== 3. 加粗检查 ===")
bolds = [(i + 1, ln.strip()[:40]) for i, ln in enumerate(lines) if "\\textbf{" in ln]
print("textbf 使用次数:", len(bolds))
for line_no, snippet in bolds:
    print(f"  L{line_no}: {snippet}")

print("\n=== 4. 超长段检查（>500字符且非命令） ===")
long_paras = []
for i, ln in enumerate(lines):
    s = ln.strip()
    if len(s) > 500 and not s.startswith("\\") and not s.startswith("%"):
        long_paras.append((i + 1, len(s), s[:50]))
print("超长段数量:", len(long_paras))
for line_no, ln, snippet in long_paras:
    print(f"  L{line_no}: {ln}字符 - {snippet}...")

print("\n=== 5. 空行统计 ===")
blank = sum(1 for ln in lines if ln.strip() == "")
print("空行数量:", blank)
