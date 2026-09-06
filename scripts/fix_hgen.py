"""Fix h_gen formula to display in CN tex (L161)."""

from pathlib import Path

CN = Path("paper_cn/main.tex")
cn = CN.read_text(encoding="utf-8")
BS = chr(92)

old = (
    "解$"
    + BS
    + "tau^2 = (h"
    + BS
    + "delta R/R)^2 + (1+R/k)/(I_0(R-1))$得$"
    + "h_{"
    + BS
    + "text{gen}} "
    + BS
    + "approx (R/"
    + BS
    + "delta R)"
    + BS
    + "sqrt{"
    + BS
    + "tau^2 - "
    + BS
    + "frac{1+R/k}{I_0(R-1)}}$"
)
new = (
    "解"
    + BS
    + "begin{equation}"
    + BS
    + "h_{"
    + BS
    + "text{gen}} "
    + BS
    + "approx (R/"
    + BS
    + "delta R)"
    + BS
    + "sqrt{"
    + BS
    + "tau^2 - "
    + BS
    + "frac{1+R/k}{I_0(R-1)}}"
    + BS
    + "end{equation}"
)
if old in cn:
    cn = cn.replace(old, new)
    CN.write_text(cn, encoding="utf-8")
    print("h_gen display OK")
else:
    print("h_gen still NOT FOUND; searching variant...")
    # try simpler: just the h_gen equation part
    simple_old = (
        "$h_{"
        + BS
        + "text{gen}} "
        + BS
        + "approx (R/"
        + BS
        + "delta R)"
        + BS
        + "sqrt{"
        + BS
        + "tau^2 - "
        + BS
        + "frac{1+R/k}{I_0(R-1)}}$"
    )
    simple_new = (
        BS
        + "begin{equation}"
        + BS
        + "h_{"
        + BS
        + "text{gen}} "
        + BS
        + "approx (R/"
        + BS
        + "delta R)"
        + BS
        + "sqrt{"
        + BS
        + "tau^2 - "
        + BS
        + "frac{1+R/k}{I_0(R-1)}}"
        + BS
        + "end{equation}"
    )
    if simple_old in cn:
        cn = cn.replace(simple_old, simple_new)
        CN.write_text(cn, encoding="utf-8")
        print("h_gen display OK (simple variant)")
    else:
        print("h_gen NOT FOUND in either form")
