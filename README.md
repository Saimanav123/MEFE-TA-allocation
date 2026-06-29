# MEFE Matching — Fair TA Allocation Made Practical

> A desktop GUI and web app that implements **Merit-based Envy-Free Egalitarian (MEFE) Matching** for allocating Teaching Assistants to courses — bridging rigorous theoretical results from computational social choice into a one-click tool for academic departments.
---

## The Problem

Manual TA allocation fails on three fronts simultaneously:

- **No fairness guarantee** — ad-hoc processes ignore TA preferences and grades together
- **Envy and resentment** — TAs get assigned to courses they dislike, even when better-qualified peers took those slots
- **Course quality suffers** — courses may receive TAs whose utility to the instructor falls below an acceptable threshold

A valid MEFE matching must satisfy all three of:

| Criterion | Meaning |
|---|---|
| **Feasibility** | Every course is assigned exactly its required number of TAs |
| **Course Satisfaction** | Average instructor utility across assigned TAs ≥ threshold *k* |
| **Merit-based Envy-Freeness** | No TA envies another TA's assignment if they have an equal or higher grade in that course |

The general problem is **NP-hard**. This tool implements seven polynomial-time and FPT algorithms that cover tractable structural cases and uses smart auto-selection to route each uploaded dataset to the right one.

---

## Features

- **Upload Excel** — one file with six sheets covers courses, TAs, all three matrices, and threshold *k*
- **Smart auto-selection** — the system analyses your data shape and recommends the optimal engine; non-expert users never need to read a theorem
- **Seven matching engines** — polynomial-time, FPT, and approximation algorithms from the paper, all hidden behind user-friendly strategy names
- **Three validity checks** — Feasibility, Satisfaction, and Envy-Freeness verified and displayed per run
- **Bipartite graph visualisation** — per-component graphs with matched edges highlighted, toggle before/after matching, overlay TA utility / course utility / grades on edges
- **Export to Excel** — matching result and validity report in a formatted workbook
- **Sample file generator** — download a correctly structured sample to get started immediately
- **Two interfaces** — a full PyQt5 desktop app (`main.py`) and a Flask web app (`webapp.py`)

---

## Quickstart

### Desktop GUI (PyQt5)

```bash
# 1. Clone
git clone https://github.com/Saimanav123/MEFE-TA-allocation.git
cd TempDC

# 2. Install dependencies
pip install PyQt5 pandas networkx matplotlib openpyxl

# 3. Run
python main.py
```

### Web App (Flask)

```bash
# 1. Install web dependencies
pip install -r requirements-web.txt   # flask pandas openpyxl networkx

# 2. Run
python webapp.py

# 3. Open http://localhost:5000 in your browser
```

---

## Excel Input Format

Your workbook must have **exactly six sheets**, in this order:

| Sheet | Name (suggested) | Contents |
|---|---|---|
| 1 | `Courses` | Two columns: Course Name, Capacity |
| 2 | `TAs` | One column: TA Name |
| 3 | `Grade_g` | Matrix — rows = TAs, columns = Courses. `g[ta][course]` = TA's grade in that course |
| 4 | `TA_Utility_u` | Matrix — rows = TAs, columns = Courses. `u[ta][course]` = TA's preference for the course (0 = not interested) |
| 5 | `Course_Utility_v` | Matrix — rows = Courses, columns = TAs. `v[course][ta]` = instructor's utility for that TA (0 only if TA utility is also 0) |
| 6 | `Threshold_k` | Single cell: the minimum average utility *k* that every course must achieve |

A **Download Sample** button inside the app generates a correctly structured example workbook you can fill in.

---

## Matching Strategies (User-Facing)

The strategy panel presents five options. The system analyses uploaded data and highlights the recommended one automatically:

| Strategy | When to use |
|---|---|
| **Auto Select** *(Recommended)* | Default for most users; the app picks the best engine based on data shape |
| **Fast Matching** | Large datasets or when each TA applies to only a few courses |
| **High Accuracy Matching** | Preference-rich data where quality alignment matters most |
| **Try All Methods** | Small datasets where comparing every engine is practical |
| **Custom (Advanced)** | Manual override to force a specific internal engine |

---

## The Seven Matching Engines

Each strategy maps internally to one or more of these theorem-backed engines, selected by the auto-routing logic without exposing theorem names to the user:

| Engine name (internal) | Paper theorem | Structural precondition | Complexity |
|---|---|---|---|
| Balanced Matching | Theorem 4 | degree − capacity ≤ 1 for every course | O(m²n²) |
| Preference-First | Theorem 5 | Capacity = 1 for all courses; each TA has strictly distinct utilities | O(nm²) |
| Quick Single-Choice | Theorem 6 | Every TA positively values at most one course (TA degree ≤ 1) | O(m log m) |
| Deep Search | Theorem 7 | Number of courses *n* and all capacities are small constants | O(m^O(1)) |
| Exhaustive Search | Theorem 9 | FPT parameterised by *m*; only practical for m ≤ 10 | O((n+1)^m) |
| Exchange-Based | Theorem 12 | Binary TA utilities {0, a}; course utility = TA grade; Hall's condition holds | Polynomial |
| Full Preference | Theorem 13 | All TA–course pairs positively value each other; strict distinct preferences | Polynomial (HR reduction) |

When multiple engines are applicable, the auto-routing logic tries them in priority order and returns the first valid MEFE matching found.

### Algorithm details

**Theorem 4 — Balanced Matching**: Decomposes the bipartite TA–course graph into connected components and handles three structural cases — forced assignments (degree = capacity), tree components (one unassigned TA), and single-cycle components (two candidate exclusions). Multiple cycles imply a no-instance.

**Theorem 5 — Preference-First**: Reduces to Weighted Strongly Stable Matching with Ties and Incomplete Lists (WSSMTI). Course preference lists ordered by TA grade; TA preference lists ordered strictly by utility. Runs Gale-Shapley (TAs propose).

**Theorem 6 — Quick Single-Choice**: Because each TA values at most one course, sub-instances are independent. Sorts TAs by grade per course, assigns the top *capacity* many. Unique solution when a solution exists.

**Theorem 7 — Deep Search**: Backtracking enumeration over all feasible TA–course assignments, pruned by MEFE validity check at each complete assignment.

**Theorem 9 — Exhaustive Search**: Full brute-force over the product of each TA's options. Hard-limited to 2 000 000 combinations to prevent hangs; warns and aborts on larger instances.

**Theorem 12 — Exchange Matching**: Finds an initial feasible matching via max-flow (NetworkX), then iteratively exchanges the lowest-grade matched TA with the highest-grade unmatched envious TA until no merit-based envy remains. Termination proven via a strictly decreasing potential function.

**Theorem 13 — Full Preference**: Reduces to the Hospital–Residents (HR) problem. Residents = TAs; Hospitals = Courses. Preference lists built from TA utilities and TA grades respectively. Runs Gale-Shapley (residents/TAs propose). Always has a solution under the stated preconditions.

---

## Project Structure

```
TempDC/
├── main.py              # Desktop GUI — PyQt5 app (algorithms + full UI)
├── webapp.py            # Web app — Flask server (reuses backend from main.py)
├── requirements-web.txt # Web-only dependencies
├── templates/
│   └── index.html       # Jinja2 template for the web interface
├── static/
│   ├── app.js           # Frontend JS for the web app
│   └── style.css        # Stylesheet for the web app
└── uploads/             # Uploaded Excel files (auto-created at runtime)
```

`webapp.py` loads the algorithm backend from `main.py` by slicing out the non-GUI portion at import time, so all matching logic lives in one place.

---

## Validation Output

After every run, three checks are displayed:

| Check | What it verifies |
|---|---|
| **Feasibility** | `|µ⁻¹(course)| == capacity` for every course |
| **Satisfaction** | `AvgUtil(course) = Σ v(course,ta) / capacity ≥ k` for every course |
| **Envy-Freeness** | No TA *tᵢ* has `g(tᵢ, course_j) ≥ g(tⱼ, course_j)` and `u(tᵢ, course_j) > u(tᵢ, own_course)` |

All three must pass for a matching to be accepted and exported.

---

## Research Background

This project implements the full complexity landscape from the paper:

**Hardness results** (general case is NP-complete):
- Two courses with identical valuations and TA degree 2 (Theorem 1, reduction from Equal-Cardinality Partition)
- Degree-3 courses and TAs, capacity 1 (Theorem 2, reduction from (3,3)-com-smti)
- Binary TA valuations, capacity 2, degree 6 (Theorem 3, reduction from 3D Perfect Matching)

**Polynomial algorithms** cover instances where the hardness conditions are relaxed — balanced degree-capacity difference, single-choice TAs, small constant parameters, or bi-valued course utilities.

**Parameterised algorithms** provide FPT solutions with respect to *m* (Theorem 9) and *n* (Theorem 10), plus a (1−ε)-approximation scheme in FPT(n, ε) when the course satisfaction threshold can be relaxed slightly (Theorem 11).

Paper preprint: Jain P., Jha P., Solanki S. — *Fairness and Efficiency in Two-Sided Matching Markets* (2025)

---

## Acknowledgements

Implemented under the guidance of **Dr. Pallavi Jain** (Department of Computer Science and SAIDE, IIT Jodhpur), corresponding author of the underlying research paper -- 

> *Fairness and Efficiency in Two-Sided Matching Markets* — Pallavi Jain, Palash Jha, Shubham Solanki (IIT Jodhpur, 2025)

---

## Dependencies

**Desktop GUI**
```
PyQt5
pandas
networkx
matplotlib
openpyxl
```

**Web App**
```
flask
pandas
networkx
openpyxl
```
