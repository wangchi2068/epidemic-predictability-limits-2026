"""Repair broken \\ref escapes in paper_en/main.tex.

The earlier heredoc replacement turned '\\\\ref{...}' into '\\r\\nef{...}' (a
carriage-return + newline + 'ef{...}'). Repair: within the run of text after
'Section~' or before '{', restore the backslash so 'ef{key}' becomes
'\\ref{key}', and strip stray carriage returns.
"""

import re
from pathlib import Path

P = Path("paper_en/main.tex")
t = P.read_text(encoding="utf-8")

# 1) collapse CR/LF pairs and stray CR to single LF
t = t.replace("\r\n", "\n").replace("\r", "\n")

# 2) fix 'ef{...}' that should be '\\ref{...}' — appears after 'Section~' or standalone
#    pattern: '~ef{key}' or start-of-context 'ef{key}'
t = re.sub(r"~ef\{", r"~\\ref{", t)
t = re.sub(r"(?<![A-Za-z])ef\{", r"\\ref{", t)

# 3) also fix any remaining '\\ef{' (backslash+ef) left from earlier pass
t = t.replace("\\ef{", "\\ref{")

# 4) verify: report any remaining bare 'ef{' not preceded by 'r'
bad = [m.start() for m in re.finditer(r"(?<!r)ef\{", t)]
print("remaining bare ef{ count:", len(bad))

P.write_text(t, encoding="utf-8")
print("repaired")
