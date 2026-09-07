"""Convert selected inline proof formulas to display (equation env) in CN tex.

Targets (proof-stage formulas currently inline in sentences):
- L161 h* approximation final step
- L233 Fisher information I(R)
- L253 log-forecast decomposition + total variance
- L272 delta-method log variance
"""

from pathlib import Path

CN = Path("paper_cn/main.tex")
cn = CN.read_text(encoding="utf-8")
BS = chr(92)

edits = []

# 1) L161: h_gen approx -> display
old1 = (
    "解$" + BS + "tau^2 = (h" + BS + "delta R/R)^2 + (1+R/k)/(" + BS + "text{floor})$"
)  # placeholder check
# Direct string: 解$\tau^2 = (h\delta R/R)^2 + (1+R/k)/(I_0(R-1))$得$h_{\text{gen}} \approx ...
seg1_old = (
    "解$"
    + BS
    + "tau^2 = (h"
    + BS
    + "delta R/R)^2 + (1+R/k)/(I_0(R-1))$得$h_{"
    + BS
    + "text{gen}} "
    + BS
    + "approx ("
    + BS
    + "frac{R}{"
    + BS
    + "delta R})"
    + BS
    + "sqrt{"
    + BS
    + "tau^2 - "
    + BS
    + "frac{1+R/k}{I_0(R-1)}}$"
)
seg1_new = (
    "解得"
    + BS
    + "begin{equation}"
    + BS
    + "h_{"
    + BS
    + "text{gen}} "
    + BS
    + "approx "
    + BS
    + "frac{R}{"
    + BS
    + "delta R}"
    + BS
    + "sqrt{"
    + BS
    + "tau^2 - "
    + BS
    + "frac{1+R/k}{I_0(R-1)}}"
    + BS
    + "end{equation}"
)
if seg1_old in cn:
    cn = cn.replace(seg1_old, seg1_new)
    print("1) h_gen display OK")
else:
    print("1) h_gen NOT FOUND")

# 2) L233: Fisher I(R) -> display
seg2_old = (
    "得$I(R) = -"
    + BS
    + "mathbb{E}["
    + BS
    + "partial^2"
    + BS
    + "ell/"
    + BS
    + "partial R^2] = "
    + BS
    + "sum_i "
    + BS
    + "mathbb{E}[x_i/R^2 - (x_i+k)/(R+k)^2] = C(1/R - 1/(R+k)) = C "
    + BS
    + "cdot k/(R(R+k))$"
)
seg2_new = (
    "得"
    + BS
    + "begin{equation}"
    + BS
    + "I(R) = -"
    + BS
    + "mathbb{E}["
    + BS
    + "partial^2"
    + BS
    + "ell/"
    + BS
    + "partial R^2] = "
    + BS
    + "sum_i "
    + BS
    + "mathbb{E}[x_i/R^2 - (x_i+k)/(R+k)^2] = C(1/R - 1/(R+k)) = C "
    + BS
    + "cdot k/(R(R+k))"
    + BS
    + "end{equation}"
)
if seg2_old in cn:
    cn = cn.replace(seg2_old, seg2_new)
    print("2) Fisher I(R) display OK")
else:
    print("2) Fisher I(R) NOT FOUND")

# 3) L253: total variance -> display
seg3_old = "总和$" + BS + "sim h v^2 + h/k = h(v^2 + 1/k)$"
seg3_new = (
    "总和"
    + BS
    + "begin{equation}"
    + BS
    + "sim h v^2 + h/k = h(v^2 + 1/k)"
    + BS
    + "end{equation}"
)
if seg3_old in cn:
    cn = cn.replace(seg3_old, seg3_new)
    print("3) total variance display OK")
else:
    print("3) total variance NOT FOUND")

# 4) L272: delta-method log variance -> display
seg4_old = (
    "写$"
    + BS
    + "log "
    + BS
    + "hat{I}_h "
    + BS
    + "approx "
    + BS
    + "log "
    + BS
    + "mathbb{E}[Z_h] + (Z_h - "
    + BS
    + "mathbb{E}[Z_h])/"
    + BS
    + "mathbb{E}[Z_h]$"
)
seg4_new = (
    "写"
    + BS
    + "begin{equation}"
    + BS
    + "log "
    + BS
    + "hat{I}_h "
    + BS
    + "approx "
    + BS
    + "log "
    + BS
    + "mathbb{E}[Z_h] + (Z_h - "
    + BS
    + "mathbb{E}[Z_h])/"
    + BS
    + "mathbb{E}[Z_h]"
    + BS
    + "end{equation}"
)
if seg4_old in cn:
    cn = cn.replace(seg4_old, seg4_new)
    print("4) delta-method display OK")
else:
    print("4) delta-method NOT FOUND")

CN.write_text(cn, encoding="utf-8")
print("done")
