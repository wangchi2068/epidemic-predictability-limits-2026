"""IMRaD reorganization for paper_en/main.tex.

Reads blocks by line ranges (1-based, inclusive), reassembles them under a new
section skeleton. Block content is preserved verbatim; only section titles and
ordering change. Back up first.
"""

import re
from pathlib import Path

P = Path("paper_en/main.tex")
lines = P.read_text(encoding="utf-8").split("\n")


def block(a, b):
    """Lines a..b (1-based inclusive) as a string."""
    return "\n".join(lines[a - 1 : b])


# --- section headers (replacement titles) ---
H_INTRO = r"\section{Introduction}" + "\n"
H_METHODS = r"\section{Methods}" + "\n"
H_RESULTS = r"\section{Results}" + "\n"
H_DISC = r"\section{Discussion}" + "\n"
H_LIM = r"\section{Limitations}" + "\n"
H_CONC = r"\section{Conclusion}" + "\n"

# --- intro block: lines 37-60 (Introduction + Related Work), keep as-is ---
intro = block(37, 60)

# --- Model and Notation block: 61-110, retitled as Methods 2.2 ---
model = block(61, 110)
model = re.sub(
    r"\\section\{Model and Notation\}", r"\\subsection{Model and assumptions}", model
)
# demote subsections
model = model.replace(
    r"\subsection{Standing assumptions}", r"\subsubsection{Standing assumptions}"
)
model = model.replace(
    r"\subsection{Modeling framework}", r"\subsubsection{Modeling framework}"
)
model = model.replace(
    r"\subsection{Relation to compartmental models}",
    r"\subsubsection{Relation to compartmental models}",
)

# --- Main Results block: 111-345 (Lemma1..population floor), retitled as Methods 2.3-2.6 ---
results_block = block(111, 345)
results_block = re.sub(
    r"\\section\{Main Results\}",
    r"\\subsection{Error decomposition and horizon}",
    results_block,
)
results_block = results_block.replace(
    r"\subsection{Lemma 1: Branching-process moments}",
    r"\subsubsection{Lemma 1: Branching-process moments}",
)
results_block = results_block.replace(
    r"\subsection{Lemma 2: Parameter amplification}",
    r"\subsubsection{Lemma 2: Parameter amplification}",
)
results_block = results_block.replace(
    r"\subsection{Theorem 1: Error decomposition and horizon}",
    r"\subsubsection{Theorem 1: Error decomposition and horizon}",
)
results_block = results_block.replace(
    r"\subsection{Theorem 2: Finite-horizon accuracy boundary}",
    r"\subsubsection{Theorem 2: Finite-horizon accuracy boundary}",
)

# split results_block at Theorem 3 for the near-critical subsection
idx_t3 = results_block.find(
    r"\subsection{Theorem 3: Near-critical finite-population window}"
)
part1 = results_block[:idx_t3]  # error decomposition (Lemmas 1-2, Thm 1-2)
part2 = results_block[idx_t3:]  # Thm 3 onward

# within part2, split at Theorem 4
idx_t4 = part2.find(r"\subsection{Theorem 4: Fisher information bound")
nearcrit = part2[:idx_t4]
nearcrit = nearcrit.replace(
    r"\subsection{Theorem 3: Near-critical finite-population window}",
    r"\subsubsection{Theorem 3: Near-critical finite-population window}",
)
rest = part2[idx_t4:]

# split rest at Theorem 5
idx_t5 = rest.find(
    r"\subsection{Theorem 5: Time-varying $R$ with independent innovations}"
)
ident = rest[:idx_t5]
ident = ident.replace(
    r"\subsection{Theorem 4: Fisher information bound (likelihood-specific)}",
    r"\subsubsection{Theorem 4: Fisher information bound (likelihood-specific)}",
)
timevar = rest[idx_t5:]
timevar = timevar.replace(
    r"\subsection{Theorem 5: Time-varying $R$ with independent innovations}",
    r"\subsubsection{Theorem 5: Time-varying $R$ with independent innovations}",
)
timevar = timevar.replace(
    r"\subsection{Theorem 5R: Persistent growth-rate drift (AR(1) extension)}",
    r"\subsubsection{Theorem 5R: Persistent growth-rate drift (AR(1) extension)}",
)
timevar = timevar.replace(
    r"\subsection{Population-level noise floor}",
    r"\subsubsection{Population-level noise floor}",
)

# --- Simulation Verification block: 348-371 ---
# Monte Carlo design -> Methods 2.7; Verification summary -> Results opening
sim = block(348, 371)
idx_summary = sim.find(r"\subsection{Verification summary}")
mc_design = sim[:idx_summary]
mc_design = mc_design.replace(
    r"\section{Simulation Verification}\label{sec:simulation}", ""
)
mc_design = mc_design.replace(
    r"\subsection{Monte Carlo design}", r"\subsubsection{Simulation design}"
)
ver_summary = sim[idx_summary:]
ver_summary = ver_summary.replace(
    r"\subsection{Verification summary}", r"\subsubsection{Verification summary}"
)

# --- Machine-Learning Roles block: 372-381 -> Results 3.5/3.6 ---
ml = block(372, 381)
ml = ml.replace(r"\section{Machine-Learning Roles}\label{sec:ml}", "")
ml = ml.replace(
    r"\subsection{ML-2: Bound tightness}", r"\subsubsection{LightGBM: bound tightness}"
)
ml = ml.replace(
    r"\subsection{ML-1: Identification-floor check}",
    r"\subsubsection{Neural network (MLP): identification-floor check}",
)

# --- Real-Data Analysis block: 382-474 -> Methods 2.1 (data) + Results 3.7 (application) ---
rd = block(382, 474)
idx_illustrative = rd.find(r"\subsection{Illustrative constant-$R$ horizons}")
data_part = rd[:idx_illustrative]
data_part = data_part.replace(r"\section{Real-Data Analysis}", "")
data_part = data_part.replace(
    r"\subsection{Data sources and methods}\label{sec:data}",
    r"\subsubsection{Data}\label{sec:data}",
)
data_part = data_part.replace(
    r"\subsection{Sensitivity and limitations of real-data estimates}",
    r"\subsubsection{Sensitivity of real-data estimates}",
)
app_part = rd[idx_illustrative:]
app_part = app_part.replace(
    r"\subsection{Illustrative constant-$R$ horizons}",
    r"\subsubsection{Illustrative constant-$R$ horizons}",
)
app_part = app_part.replace(
    r"\subsection{Prospective walk-forward evaluation}",
    r"\subsubsection{Prospective walk-forward evaluation}",
)

# --- Discussion block: 475-504, split Limitations out ---
disc = block(475, 504)
idx_lim = disc.find(r"\subsection{Limitations}")
disc_main = disc[:idx_lim]
lim_part = disc[idx_lim:]
lim_part = lim_part.replace(r"\subsection{Limitations}", "")
# split remaining discussion subsections
idx_impl = disc_main.find(r"\subsection{Implications for public-health communication}")
disc_1 = disc_main[:idx_impl]  # opening paragraphs
disc_2 = disc_main[
    idx_impl:
]  # Implications + ensembles + ML + Relation to deterministic
# move ML paragraph from disc_2 to disc_1? keep simple: leave order, just retitle
disc_2 = disc_2.replace(
    r"\subsection{Implications for public-health communication}",
    r"\subsubsection{Implications for public-health communication}",
)
disc_2 = disc_2.replace(
    r"\subsection{Relation to deterministic threshold theory}",
    r"\subsubsection{Relation to deterministic threshold theory}",
)

# --- Conclusion: 505-? (before Declarations) ---
idx_decl = (
    lines.index(
        next(ln for ln in lines[504:] if ln.startswith(r"\section*{Declarations}"))
    )
    + 1
)
conc = block(505, idx_decl - 1)

# --- Declarations + bibliography: keep tail verbatim ---
tail = block(idx_decl, len(lines))

# assemble
out = []
out.append(H_INTRO)
out.append(intro)
out.append("\n")
out.append(H_METHODS)
out.append(r"\subsection{Data}" + "\n")
out.append(data_part)
out.append("\n")
out.append(r"\subsection{Model and assumptions}" + "\n")
out.append(model)
out.append("\n")
out.append(r"\subsection{Error decomposition and horizon}" + "\n")
out.append(part1)
out.append("\n")
out.append(r"\subsection{Near-critical window}" + "\n")
out.append(nearcrit)
out.append("\n")
out.append(r"\subsection{Identification floor}" + "\n")
out.append(ident)
out.append("\n")
out.append(r"\subsection{Time-varying settings and population floor}" + "\n")
out.append(timevar)
out.append("\n")
out.append(r"\subsection{Simulation design}" + "\n")
out.append(mc_design)
out.append("\n")
out.append(H_RESULTS)
out.append(r"\subsubsection{Verification summary}" + "\n")
out.append(ver_summary)
out.append("\n")
out.append(ml)
out.append("\n")
out.append(r"\subsubsection{Real-data application}" + "\n")
out.append(app_part)
out.append("\n")
out.append(H_DISC)
out.append(disc_1)
out.append("\n")
out.append(disc_2)
out.append("\n")
out.append(H_LIM)
out.append(lim_part)
out.append("\n")
out.append(H_CONC)
out.append(conc)
out.append("\n")
out.append(tail)

P.write_text("".join(out), encoding="utf-8")
print("reorganized EN, lines:", len("".join(out).split("\n")))
