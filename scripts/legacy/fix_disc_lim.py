"""Fix Discussion/Limitations ordering in paper_en/main.tex.

Current (wrong): Discussion -> Limitations -> [forecast-budget para] -> Implications -> Relation
Target:          Discussion -> [forecast-budget para] -> Implications -> Relation -> Limitations

Move the 'forecast-budget' paragraph (which starts with 'The forecast-budget framing
connects directly') from after the Limitations header to before it.
"""

from pathlib import Path

P = Path("paper_en/main.tex")
t = P.read_text(encoding="utf-8")

disc_marker = r"\section{Discussion}"
lim_marker = r"\section{Limitations}"
fb_start = "The forecast-budget framing connects directly"

i_disc = t.find(disc_marker)
i_lim = t.find(lim_marker, i_disc)
i_fb = t.find(fb_start, i_lim)
if -1 in (i_disc, i_lim, i_fb):
    raise SystemExit(f"markers not found: disc={i_disc} lim={i_lim} fb={i_fb}")

# Limitations body: from \section{Limitations} up to the forecast-budget para
lim_body = t[i_lim:i_fb]
# forecast-budget para: from its start to the next \subsection or \section
i_next = min(
    [
        x
        for x in [
            t.find(r"\subsection{Implications", i_fb),
            t.find(r"\subsection{Relation", i_fb),
            t.find(r"\section{Conclusion", i_fb),
        ]
        if x != -1
    ]
)
fb_para = t[i_fb:i_next]

# Rebuild: ... [disc body] [forecast-budget] [Implications+Relation] [Limitations body]
# Find where Implications currently starts (after fb_para's original position)
t_new = t[:i_lim] + fb_para + "\n\n" + t[i_next:] + "\n\n" + lim_body
# strip the now-duplicated Limitations header from lim_body tail? lim_body already includes it; keep once.
P.write_text(t_new, encoding="utf-8")
print("reordered Discussion/Limitations")
