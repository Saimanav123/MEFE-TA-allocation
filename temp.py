"""
smart_selection_panel.py
═══════════════════════════════════════════════════════════════════
Smart Selection Panel for MEFE Matching GUI
============================================
A guided, user-friendly algorithm-selection widget.
Users choose a plain-English "strategy"; the panel internally maps
that choice to the correct solver (theorem names are never shown).

Public API:
  panel = SmartSelectionPanel(parent)
  panel.load_data(courses, tas, capacities, ta_utility,
                  course_utility, grade, k)    # triggers auto-analysis
  key = panel.get_solver_key()                 # returns e.g. 'thm4'
  panel.strategy_selected.connect(callback)    # emits key string

For "Try All" mode call:
  panel.run_compare(solvers_dict, courses, tas, capacities,
                    grade, ta_utility, course_utility, k)
═══════════════════════════════════════════════════════════════════
"""

"""
main_integration_patch.py
══════════════════════════════════════════════════════════════════
HOW TO INTEGRATE SmartSelectionPanel INTO main.py
══════════════════════════════════════════════════════════════════

Apply the 5 numbered diffs below (each is a FIND → REPLACE block).
They are self-contained and do NOT alter any backend solver logic.
══════════════════════════════════════════════════════════════════
"""

# ──────────────────────────────────────────────────────────────────
# DIFF 1 — Add import at the top of main.py
# (after the existing PyQt5 imports block, around line 22)
# ──────────────────────────────────────────────────────────────────

# FIND (exact line):
# from PyQt5.QtGui import QColor

# REPLACE WITH:
# from PyQt5.QtGui import QColor
# from smart_selection_panel import SmartSelectionPanel


# ──────────────────────────────────────────────────────────────────
# DIFF 2 — Add smart_panel attribute in __init__
# (inside MEFEApp.__init__, after self._data = {})
# ──────────────────────────────────────────────────────────────────

# FIND:
#         self._data = {}
#         self._apply_style()
#         self._build_ui()

# REPLACE WITH:
#         self._data        = {}
#         self._smart_panel = None    # set in _tab_upload
#         self._apply_style()
#         self._build_ui()


# ──────────────────────────────────────────────────────────────────
# DIFF 3 — Add SmartSelectionPanel to the Upload tab
# (inside _tab_upload, after the summary scorecards sc_row block,
#  just before the preview tables — around line 1193)
# ──────────────────────────────────────────────────────────────────

# FIND (exact block):
#         self.prev_tabs = QTabWidget(); self.prev_tabs.setVisible(False)
#         lay.addWidget(self.prev_tabs)
#         return w

# REPLACE WITH:
#         # ── Smart Selection Panel ─────────────────────────────────
#         self._smart_panel = SmartSelectionPanel()
#         # Inject solver dict so "Try All" mode works
#         self._smart_panel.set_solvers(THEOREM_SOLVERS)
#         # When user picks a strategy, mirror it in the hidden combo
#         self._smart_panel.strategy_selected.connect(self._on_smart_select)
#
#         smart_group = QGroupBox("Choose Matching Strategy")
#         smart_group.setStyleSheet(
#             f"QGroupBox {{ color:{TEXT}; font-size:13px; font-weight:700; "
#             f"border:1px solid {BORDER}; border-radius:10px; "
#             f"margin-top:8px; padding-top:10px; }} "
#             f"QGroupBox::title {{ subcontrol-origin:margin; "
#             f"subcontrol-position:top left; padding:0 6px; }}")
#         sg_lay = QVBoxLayout(smart_group)
#         sg_lay.addWidget(self._smart_panel)
#         lay.addWidget(smart_group)
#
#         self.prev_tabs = QTabWidget(); self.prev_tabs.setVisible(False)
#         lay.addWidget(self.prev_tabs)
#         return w


# ──────────────────────────────────────────────────────────────────
# DIFF 4 — Wire the "Run Algorithm" button through the smart panel
# (inside _run, replace the thm_combo lookup block, around line 1424)
# ──────────────────────────────────────────────────────────────────

# FIND:
#         thm_idx = self.thm_combo.currentIndex()
#         thm_key = THEOREM_LABELS[thm_idx][1]
#         solver  = THEOREM_SOLVERS[thm_key]
#
#         matching, report, log, nc, nt, meta = solver(
#             d['courses'], d['tas'], d['capacities'],
#             d['grade'], d['ta_utility'], d['course_utility'], d['k'])

# REPLACE WITH:
#         # ── Resolve solver via Smart Selection Panel ─────────────
#         if self._smart_panel is not None:
#             smart_key = self._smart_panel.get_solver_key()
#         else:
#             # Fallback: use the legacy combo
#             thm_idx   = self.thm_combo.currentIndex()
#             smart_key = THEOREM_LABELS[thm_idx][1]
#
#         # Handle "Try All" compare mode
#         if smart_key == "__all__":
#             chosen = self._smart_panel.run_compare(
#                 THEOREM_SOLVERS,
#                 d['courses'], d['tas'], d['capacities'],
#                 d['grade'], d['ta_utility'], d['course_utility'], d['k'],
#                 parent_widget=self,
#             )
#             self.btn_run.setEnabled(True)
#             self.btn_run.setText("  ▶  Run Algorithm  ")
#             if chosen:
#                 smart_key = chosen   # user picked a winner from dialog
#             else:
#                 return               # closed without choosing
#
#         solver = THEOREM_SOLVERS.get(smart_key, THEOREM_SOLVERS['thm4'])
#
#         matching, report, log, nc, nt, meta = solver(
#             d['courses'], d['tas'], d['capacities'],
#             d['grade'], d['ta_utility'], d['course_utility'], d['k'])


# ──────────────────────────────────────────────────────────────────
# DIFF 5 — Trigger analysis whenever a file is loaded
# (inside _load, after self._show_previews(...), around line 1383)
# ──────────────────────────────────────────────────────────────────

# FIND:
#             self._show_previews(courses, tas, caps, grade, ta_u, cu)
#             self.btn_run.setEnabled(True)

# REPLACE WITH:
#             self._show_previews(courses, tas, caps, grade, ta_u, cu)
#             # ── Trigger smart analysis ────────────────────────────
#             if self._smart_panel is not None:
#                 self._smart_panel.load_data(
#                     courses, tas, caps, ta_u, cu, grade, k)
#             self.btn_run.setEnabled(True)


# ──────────────────────────────────────────────────────────────────
# DIFF 6 — Add _on_smart_select helper (add inside MEFEApp class,
#           e.g. right after _on_theorem_change)
# ──────────────────────────────────────────────────────────────────

# ADD this new method to MEFEApp:

# def _on_smart_select(self, solver_key: str):
#     """
#     Called when user explicitly clicks a strategy card.
#     Mirrors the choice onto the hidden legacy combo so that
#     subtitle labels etc. update correctly.
#     """
#     if solver_key in ("__all__", "__custom__"):
#         return                # handled at run-time in _run()
#     # Find matching index in THEOREM_LABELS for subtitle update
#     for idx, (_, key) in enumerate(THEOREM_LABELS):
#         if key == solver_key:
#             self.thm_combo.blockSignals(True)
#             self.thm_combo.setCurrentIndex(idx)
#             self.thm_combo.blockSignals(False)
#             self._on_theorem_change(idx)
#             break


# ══════════════════════════════════════════════════════════════════
#  QUICK VERIFICATION SCRIPT
#  Run this after patching to verify imports and wiring work.
# ══════════════════════════════════════════════════════════════════
def _verify():
    """Smoke-test: import both modules and check key wiring."""
    import importlib, sys, types

    # Quick structural checks without launching Qt
    import ast, pathlib

    panel_src = pathlib.Path("smart_selection_panel.py").read_text()
    tree = ast.parse(panel_src)

    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    expected = [
        "DataAnalyzer", "StrategyCard", "InsightBox",
        "DescriptionBar", "CustomSelectorRow",
        "CompareResultsDialog", "SmartSelectionPanel",
    ]
    for cls in expected:
        assert cls in classes, f"Missing class: {cls}"
    print("✅  All required classes found in smart_selection_panel.py")

    # Check that strategy IDs cover every THEOREM_SOLVERS key
    from smart_selection_panel import STRATEGIES, _CUSTOM_OPTIONS, _STRATEGY_FALLBACK
    custom_keys = {k for _, k in _CUSTOM_OPTIONS}
    needed = {"thm4", "thm5", "thm6", "thm7", "thm9", "thm12", "thm13"}
    assert needed <= custom_keys, f"Missing solver keys in custom options: {needed - custom_keys}"
    print("✅  All solver keys covered in Custom dropdown")

    print("\n🎉  Integration checks passed. Apply the 6 diffs to main.py and you're done.")


if __name__ == "__main__":
    _verify()












from collections import defaultdict

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QComboBox, QDialog,
    QDialogButtonBox, QTextEdit, QApplication, QGroupBox,
    QGridLayout, QToolTip,
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize, QPoint
from PyQt5.QtGui import QColor, QCursor, QFont, QPainter, QLinearGradient


# ──────────────────────────────────────────────────────────────────
#  Palette (mirrors main.py so widgets blend in)
# ──────────────────────────────────────────────────────────────────
_BG      = "#0f1117"
_PANEL   = "#1a1d2e"
_CARD    = "#21253a"
_ACCENT  = "#6c63ff"
_ACCENT2 = "#00d4aa"
_DANGER  = "#ff4757"
_TEXT    = "#e8e8f0"
_SUBTEXT = "#8888aa"
_BORDER  = "#2e3150"
_GREEN   = "#2ed573"
_GOLD    = "#ffd700"
_ORANGE  = "#ff9f43"


# ──────────────────────────────────────────────────────────────────
#  Internal strategy → solver mapping (NEVER shown to user)
# ──────────────────────────────────────────────────────────────────
# 'auto'    → resolved dynamically by DataAnalyzer
# 'fast'    → thm6  (grade-sort, O(m log m), TA degree ≤ 1)
# 'accurate'→ thm5  (Stable Matching WSSMTI) or thm13 (HR)
# 'compare' → '__all__'  (special: run every solver)
# 'custom'  → '__custom__' (special: user picks from hidden dropdown)

_STRATEGY_FALLBACK = {        # used when auto-routing fails
    'fast':     'thm6',
    'accurate': 'thm5',
}

# Friendly labels for the Custom dropdown  (NO theorem numbers shown)
_CUSTOM_OPTIONS = [
    ("Degree-Capacity Method  ·  Polynomial-time",   "thm4"),
    ("Stable Preference Matching  ·  Poly-time",     "thm5"),
    ("Grade-Priority Sort  ·  Ultra-fast",           "thm6"),
    ("Small Dataset Enumeration",                    "thm7"),
    ("Exhaustive Search  ·  Very small data only",   "thm9"),
    ("Exchange-Based Matching  ·  Existential",      "thm12"),
    ("Resident-Hospital Style Matching",             "thm13"),
]

# ──────────────────────────────────────────────────────────────────
#  Strategy definitions  (UI metadata)
# ──────────────────────────────────────────────────────────────────
STRATEGIES = [
    {
        "id":          "auto",
        "icon":        "✅",
        "title":       "Auto Select Best Method",
        "subtitle":    "Let the system choose based on your data",
        "badge":       "RECOMMENDED",
        "badge_fg":    _GREEN,
        "badge_bg":    "#0d2a1a",
        "border_sel":  _GREEN,
        "tooltip": (
            "Auto Select analyses your uploaded data and picks the fastest, "
            "most accurate algorithm that fits its properties. "
            "Ideal for everyday use — no configuration required."
        ),
        "description": (
            "The system inspects number of courses, TAs, course capacities, "
            "preference patterns, and grade distributions, then routes to "
            "the most efficient algorithm automatically. "
            "You get the best result without needing any technical knowledge."
        ),
    },
    {
        "id":          "fast",
        "icon":        "⚡",
        "title":       "Fast Matching",
        "subtitle":    "Best when each TA prefers only one course",
        "badge":       "FAST",
        "badge_fg":    _GOLD,
        "badge_bg":    "#2a2500",
        "border_sel":  _GOLD,
        "tooltip": (
            "Fast Matching: Works best when each TA has a preference for just "
            "one course. Ranks TAs by academic grade and fills each course "
            "instantly. Runs in near-linear time."
        ),
        "description": (
            "Sorts TAs by grade for each course and fills seats top-down. "
            "Extremely fast even for large datasets. "
            "Best fit: each TA only applied to one course, "
            "or you need results in milliseconds."
        ),
    },
    {
        "id":          "accurate",
        "icon":        "🎯",
        "title":       "High Accuracy Matching",
        "subtitle":    "Stable, preference-respecting assignment",
        "badge":       "PRECISE",
        "badge_fg":    _ACCENT,
        "badge_bg":    "#14103a",
        "border_sel":  _ACCENT,
        "tooltip": (
            "High Accuracy: Finds a stable matching where no TA would prefer "
            "to swap assignments with another, given their grade standing. "
            "Best when courses each need exactly 1 TA."
        ),
        "description": (
            "Applies a stability-based approach that guarantees no TA could "
            "legitimately claim another's course based on merit. "
            "Best fit: each course needs 1 TA, "
            "TAs have clearly ranked preferences."
        ),
    },
    {
        "id":          "compare",
        "icon":        "🔍",
        "title":       "Try All Methods",
        "subtitle":    "Run every approach and compare outcomes",
        "badge":       "THOROUGH",
        "badge_fg":    _ORANGE,
        "badge_bg":    "#2a1800",
        "border_sel":  _ORANGE,
        "tooltip": (
            "Try All: Runs every available matching approach on your data, "
            "then shows which ones succeed and how they differ. "
            "Takes longer but gives the most complete picture."
        ),
        "description": (
            "Executes all matching methods and presents a side-by-side "
            "comparison of which ones found valid assignments. "
            "Best fit: you want to explore options, "
            "validate results, or your data is unusual."
        ),
    },
    {
        "id":          "custom",
        "icon":        "🧪",
        "title":       "Custom Selection",
        "subtitle":    "Advanced — manually choose a specific method",
        "badge":       "ADVANCED",
        "badge_fg":    _DANGER,
        "badge_bg":    "#2a0a0a",
        "border_sel":  _DANGER,
        "tooltip": (
            "Custom: Gives you direct control over which specific algorithm "
            "to run. For power users who understand their data's properties."
        ),
        "description": (
            "Choose exactly which matching method to apply. "
            "Use this if you have domain knowledge about your dataset "
            "or want to test a specific approach."
        ),
    },
]


# ══════════════════════════════════════════════════════════════════
#  DATA ANALYSIS ENGINE  (internal — results shown in plain English)
# ══════════════════════════════════════════════════════════════════

class DataAnalyzer:
    """
    Analyses the uploaded dataset and determines the best strategy.
    All internal algorithm names are hidden; only plain-English
    insight strings are surfaced.
    """

    def __init__(self, courses, tas, capacities,
                 ta_utility, course_utility, grade, k):
        self.courses        = courses
        self.tas            = tas
        self.capacities     = capacities
        self.ta_utility     = ta_utility
        self.course_utility = course_utility
        self.grade          = grade
        self.k              = k

        self.nc, self.nt = self._build_graph()
        self._run_analysis()

    # ── Graph helper ──────────────────────────────────────────────
    def _build_graph(self):
        nc, nt = defaultdict(set), defaultdict(set)
        for (ta, c), u in self.ta_utility.items():
            if u != 0:
                nc[c].add(ta)
                nt[ta].add(c)
        return dict(nc), dict(nt)

    # ── Core metrics computation ──────────────────────────────────
    def _run_analysis(self):
        n = len(self.courses)
        m = len(self.tas)

        # TA degree stats
        ta_degrees = [len(self.nt.get(ta, set())) for ta in self.tas]
        self.max_ta_degree = max(ta_degrees, default=0)
        self.avg_ta_degree = sum(ta_degrees) / m if m > 0 else 0.0

        # Course degree-capacity difference
        diffs = [len(self.nc.get(c, set())) - self.capacities[c]
                 for c in self.courses]
        self.max_diff = max(diffs, default=0)
        self.min_diff = min(diffs, default=0)

        # Capacity stats
        caps = list(self.capacities.values())
        self.all_cap_one  = all(v == 1 for v in caps)
        self.max_cap      = max(caps, default=1)
        self.total_cap    = sum(caps)
        self.constant_cap = len(set(caps)) == 1

        # Distinct TA utilities?  (each TA ranks positively-valued courses differently)
        self.distinct_ta_utils = all(
            self._ta_has_distinct_pos_utils(ta) for ta in self.tas
        )

        # Binary TA utilities? (each TA only uses 0 / one positive value)
        self.binary_ta_utils = all(
            len({self.ta_utility.get((ta, c), 0)
                 for c in self.courses
                 if self.ta_utility.get((ta, c), 0) > 0}) <= 1
            for ta in self.tas
        )

        # No grade ties per course?
        self.distinct_grades = self._check_grade_distinctness()

        # All TAs value all courses positively?
        self.all_positive = all(
            self.ta_utility.get((ta, c), 0) > 0
            for ta in self.tas for c in self.courses
        )

        # Course utility == grade?
        self.util_equals_grade = all(
            abs(self.course_utility.get((c, ta), 0)
                - self.grade.get((ta, c), 0)) < 1e-9
            for ta in self.tas for c in self.courses
        )

        # Data-size buckets
        self.is_tiny   = m <= 6  and n <= 3
        self.is_small  = m <= 12 and n <= 5
        self.n, self.m = n, m

    def _ta_has_distinct_pos_utils(self, ta):
        pos = [self.ta_utility.get((ta, c), 0)
               for c in self.courses
               if self.ta_utility.get((ta, c), 0) > 0]
        return len(pos) == len(set(pos))

    def _check_grade_distinctness(self):
        for c in self.courses:
            gs = [self.grade.get((ta, c), 0)
                  for ta in self.tas
                  if self.ta_utility.get((ta, c), 0) > 0]
            if len(gs) != len(set(gs)):
                return False
        return True

    # ── Public: recommendation + insights ────────────────────────
    def get_recommendation(self):
        """Returns (strategy_id, reason_text, [insight_strings])."""
        strategy, reason = self._pick_strategy()
        insights         = self._build_insights()
        return strategy, reason, insights

    def get_auto_solver_key(self):
        """
        For the 'auto' strategy: return the specific internal solver key.
        This logic is completely hidden from the user.
        """
        # Priority cascade — fastest/most precise first
        if self.max_ta_degree <= 1:
            return 'thm6'          # O(m log m) sort
        if self.min_diff >= 0 and self.max_diff <= 1:
            return 'thm4'          # degree-capacity poly-time
        if self.all_cap_one and self.distinct_ta_utils:
            return 'thm5'          # stable matching
        if self.all_positive and self.distinct_ta_utils and self.distinct_grades:
            return 'thm13'         # hospital-residents
        if self.is_small:
            return 'thm7'          # enumeration
        if self.is_tiny:
            return 'thm9'          # brute-force (safe for very small)
        return 'thm4'              # safest general fallback

    # ── Private: strategy selection logic ─────────────────────────
    def _pick_strategy(self):
        n, m = self.n, self.m

        if self.is_tiny:
            return ('auto',
                    f"Your dataset is very small ({n} courses, {m} TAs). "
                    "Any method will run instantly. "
                    "Auto Select will pick the fastest option for you.")

        if self.max_ta_degree <= 1:
            return ('fast',
                    "Each TA applies to at most one course. "
                    "Fast Matching handles this perfectly — it ranks TAs "
                    "by grade and fills each course in milliseconds.")

        if self.all_cap_one and self.distinct_ta_utils and self.distinct_grades:
            return ('accurate',
                    "Every course needs exactly 1 TA, TAs have clearly "
                    "ranked preferences, and grades are all distinct. "
                    "High Accuracy Matching guarantees a perfectly "
                    "stable, fair assignment.")

        if self.min_diff >= 0 and self.max_diff <= 1:
            return ('auto',
                    "The number of eligible TAs for each course is at most "
                    "1 more than required. "
                    "Auto Select will use a highly efficient structural "
                    "algorithm suited to this pattern.")

        if self.all_positive and self.distinct_ta_utils and self.distinct_grades:
            return ('accurate',
                    "All TAs and courses value each other, with distinct "
                    "preferences and grades throughout. "
                    "High Accuracy Matching is guaranteed to find a valid "
                    "result under these conditions.")

        if self.is_small:
            return ('auto',
                    f"Your dataset ({n} courses, {m} TAs) is small enough "
                    "for a thorough search. Auto Select will explore the "
                    "solution space efficiently.")

        return ('compare',
                "Your data has complex or varied preference patterns. "
                "Trying all methods will reveal which ones produce valid "
                "assignments for your specific setup.")

    # ── Plain-English insight builder ─────────────────────────────
    def _build_insights(self):
        ins = []
        n, m = self.n, self.m

        ins.append(("📊", f"{n} course{'s' if n!=1 else ''} · "
                          f"{m} TA{'s' if m!=1 else ''} · "
                          f"k = {self.k}"))

        if self.max_ta_degree == 0:
            ins.append(("⚠️", "No TA has any course preference"))
        elif self.max_ta_degree == 1:
            ins.append(("🎓", "Each TA applies to exactly one course"))
        elif self.avg_ta_degree < 2.5:
            ins.append(("🎓", f"TAs apply to ~{self.avg_ta_degree:.1f} courses on average"))
        else:
            ins.append(("🎓", f"TAs have broad preferences "
                              f"(avg {self.avg_ta_degree:.1f} courses)"))

        if self.all_cap_one:
            ins.append(("📌", "Every course needs exactly 1 TA"))
        elif self.constant_cap:
            ins.append(("📌", f"All courses need {self.max_cap} TAs each"))
        else:
            ins.append(("📌", f"Courses need 1–{self.max_cap} TAs each"))

        if self.max_diff <= 1 and self.min_diff >= 0:
            ins.append(("🔗", "Course supply closely matches demand (≤1 extra TA)"))

        if self.distinct_grades:
            ins.append(("🏆", "Grades uniquely rank all TAs per course"))
        else:
            ins.append(("⚠️", "Some TAs share the same grade in a course"))

        if self.distinct_ta_utils:
            ins.append(("📋", "TAs have clearly ranked course preferences"))

        if self.binary_ta_utils:
            ins.append(("🔲", "TA preferences are binary (like / dislike)"))

        if self.all_positive:
            ins.append(("💚", "All TAs are eligible for all courses"))

        size_tag = ("🔬 Very small" if self.is_tiny
                    else "✅ Small" if self.is_small
                    else "📦 Medium/large")
        ins.append((size_tag.split()[0],
                    f"{size_tag.split(None, 1)[1]} dataset "
                    f"({m} TAs, {n} courses)"))

        return ins


# ══════════════════════════════════════════════════════════════════
#  STRATEGY CARD  (individual clickable option tile)
# ══════════════════════════════════════════════════════════════════

class StrategyCard(QFrame):
    """
    A clickable card representing one matching strategy.
    Highlights on hover, shows richer selected state,
    and draws a green "Recommended" banner when flagged.
    """

    clicked_signal = pyqtSignal(str)   # emits strategy id

    def __init__(self, strategy: dict, parent=None):
        super().__init__(parent)
        self.strategy       = strategy
        self._sid           = strategy["id"]
        self._selected      = False
        self._recommended   = False
        self._hovered       = False

        self.setFixedHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setToolTip(strategy["tooltip"])

        self._build_layout()
        self._refresh_style()

    # ── Layout ────────────────────────────────────────────────────
    def _build_layout(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 12, 16, 12)
        outer.setSpacing(14)

        # Left: big icon
        icon_lbl = QLabel(self.strategy["icon"])
        icon_lbl.setFixedWidth(46)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(
            "font-size:30px; background:transparent; border:none;")
        outer.addWidget(icon_lbl)

        # Centre: title + subtitle
        text_col = QVBoxLayout()
        text_col.setSpacing(3)

        self._title_lbl = QLabel(self.strategy["title"])
        self._title_lbl.setStyleSheet(
            f"font-size:14px; font-weight:700; color:{_TEXT}; "
            "background:transparent; border:none;")

        self._sub_lbl = QLabel(self.strategy["subtitle"])
        self._sub_lbl.setStyleSheet(
            f"font-size:11px; color:{_SUBTEXT}; "
            "background:transparent; border:none;")

        text_col.addWidget(self._title_lbl)
        text_col.addWidget(self._sub_lbl)
        outer.addLayout(text_col, stretch=1)

        # Right: badge + recommended star
        right_col = QVBoxLayout()
        right_col.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        right_col.setSpacing(4)

        badge_txt = self.strategy["badge"]
        self._badge = QLabel(badge_txt)
        self._badge.setAlignment(Qt.AlignCenter)
        self._badge.setFixedWidth(100)
        self._badge.setStyleSheet(
            f"background:{self.strategy['badge_bg']}; "
            f"color:{self.strategy['badge_fg']}; "
            "border-radius:10px; padding:3px 8px; "
            "font-size:10px; font-weight:700; border:none;")
        right_col.addWidget(self._badge)

        self._rec_lbl = QLabel("★ System pick")
        self._rec_lbl.setAlignment(Qt.AlignCenter)
        self._rec_lbl.setStyleSheet(
            f"color:{_GREEN}; font-size:10px; font-weight:600; "
            "background:transparent; border:none;")
        self._rec_lbl.setVisible(False)
        right_col.addWidget(self._rec_lbl)

        outer.addLayout(right_col)

    # ── Style helpers ─────────────────────────────────────────────
    def _refresh_style(self):
        border_col   = self.strategy["border_sel"] if self._selected else _BORDER
        border_width = 2 if self._selected else 1
        bg           = _CARD

        if self._selected:
            bg = self._darken(self.strategy["border_sel"], 0.10)
        elif self._hovered:
            bg = "#272b40"

        self.setStyleSheet(
            f"QFrame {{"
            f"  background:{bg};"
            f"  border:{border_width}px solid {border_col};"
            f"  border-radius:12px;"
            f"}}"
        )

    @staticmethod
    def _darken(hex_color: str, amount: float) -> str:
        """Mix hex_color with black by `amount` (0–1)."""
        c = QColor(hex_color)
        r = int(c.red()   * amount)
        g = int(c.green() * amount)
        b = int(c.blue()  * amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ── Public setters ────────────────────────────────────────────
    def set_selected(self, val: bool):
        self._selected = val
        self._refresh_style()

    def set_recommended(self, val: bool):
        self._recommended = val
        self._rec_lbl.setVisible(val)
        if val:
            # Pulse the badge colour to green tint
            self._badge.setStyleSheet(
                f"background:#0d2a1a; color:{_GREEN}; "
                "border-radius:10px; padding:3px 8px; "
                "font-size:10px; font-weight:700; "
                f"border:1px solid {_GREEN};")

    # ── Mouse events ──────────────────────────────────────────────
    def enterEvent(self, _):
        self._hovered = True
        self._refresh_style()

    def leaveEvent(self, _):
        self._hovered = False
        self._refresh_style()

    def mousePressEvent(self, _):
        self.clicked_signal.emit(self._sid)


# ══════════════════════════════════════════════════════════════════
#  INSIGHT BOX  (shows detected data properties as pill badges)
# ══════════════════════════════════════════════════════════════════

class InsightBox(QFrame):
    """
    Displays auto-detected dataset properties as pill-shaped badges.
    Also shows the recommendation reason and "Why?" expandable text.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"QFrame {{ background:{_PANEL}; border:1px solid {_BORDER}; "
            "border-radius:10px; }}")

        main = QVBoxLayout(self)
        main.setContentsMargins(14, 10, 14, 10)
        main.setSpacing(8)

        # Header row
        hdr = QHBoxLayout()
        title = QLabel("💡  Data Insights")
        title.setStyleSheet(
            f"color:{_ACCENT2}; font-size:12px; font-weight:700; "
            "background:transparent; border:none;")
        hdr.addWidget(title)
        hdr.addStretch()

        self._why_btn = QPushButton("Why this recommendation? ▾")
        self._why_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._why_btn.setStyleSheet(
            f"color:{_SUBTEXT}; font-size:11px; background:transparent; "
            "border:none; text-decoration:underline;")
        self._why_btn.clicked.connect(self._toggle_why)
        hdr.addWidget(self._why_btn)
        main.addLayout(hdr)

        # Pill badges area
        self._badge_row = QHBoxLayout()
        self._badge_row.setSpacing(6)
        self._badge_row.setAlignment(Qt.AlignLeft)
        main.addLayout(self._badge_row)

        # Recommendation summary line
        self._rec_lbl = QLabel("")
        self._rec_lbl.setWordWrap(True)
        self._rec_lbl.setStyleSheet(
            f"color:{_GREEN}; font-size:11px; font-style:italic; "
            "background:transparent; border:none; padding-top:4px;")
        main.addWidget(self._rec_lbl)

        # Expandable "Why?" text
        self._why_panel = QLabel("")
        self._why_panel.setWordWrap(True)
        self._why_panel.setVisible(False)
        self._why_panel.setStyleSheet(
            f"color:{_TEXT}; font-size:11px; "
            f"background:{_CARD}; border:1px solid {_BORDER}; "
            "border-radius:8px; padding:8px; margin-top:4px;")
        main.addWidget(self._why_panel)

        self._why_visible = False

    def update(self, insights: list, rec_strategy: str,
               rec_reason: str, strategy_desc: str):
        """Refresh all insight badges and recommendation text."""
        # Clear old badges
        while self._badge_row.count():
            item = self._badge_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new pill badges
        for (emoji, text) in insights:
            pill = QLabel(f"  {emoji} {text}  ")
            pill.setStyleSheet(
                f"background:{_CARD}; color:{_TEXT}; "
                "border-radius:10px; font-size:11px; padding:3px 2px; "
                f"border:1px solid {_BORDER};")
            self._badge_row.addWidget(pill)
        self._badge_row.addStretch()

        # Update recommendation text
        strategy_title = next(
            (s["title"] for s in STRATEGIES if s["id"] == rec_strategy),
            "Auto Select Best Method"
        )
        self._rec_lbl.setText(f"→  Recommendation: {strategy_title}")
        self._why_panel.setText(rec_reason)
        self._why_btn.setVisible(bool(rec_reason))

    def _toggle_why(self):
        self._why_visible = not self._why_visible
        self._why_panel.setVisible(self._why_visible)
        self._why_btn.setText(
            "Why this recommendation? ▴" if self._why_visible
            else "Why this recommendation? ▾"
        )


# ══════════════════════════════════════════════════════════════════
#  DESCRIPTION BAR  (shows detail text for selected strategy)
# ══════════════════════════════════════════════════════════════════

class DescriptionBar(QLabel):
    """One-line (wrapping) description shown below the selected card."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWordWrap(True)
        self.setMinimumHeight(36)
        self.setStyleSheet(
            f"color:{_SUBTEXT}; font-size:11px; font-style:italic; "
            f"background:{_CARD}; border-radius:8px; "
            f"border:1px solid {_BORDER}; padding:8px 12px;")
        self.setText("Select a matching strategy above to see details.")


# ══════════════════════════════════════════════════════════════════
#  CUSTOM SELECTOR  (hidden inside "Custom" strategy)
# ══════════════════════════════════════════════════════════════════

class CustomSelectorRow(QWidget):
    """
    A row containing a friendly dropdown for advanced users.
    Algorithm keys are never shown; only friendly labels.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 4, 0, 0)
        row.setSpacing(10)

        lbl = QLabel("Select method:")
        lbl.setStyleSheet(
            f"color:{_TEXT}; font-size:12px; "
            "font-weight:600; background:transparent;")
        row.addWidget(lbl)

        self._combo = QComboBox()
        for display, _ in _CUSTOM_OPTIONS:
            self._combo.addItem(display)
        self._combo.setMinimumWidth(340)
        self._combo.setStyleSheet(
            f"QComboBox {{ background:{_CARD}; color:{_TEXT}; "
            f"border:1px solid {_BORDER}; border-radius:6px; "
            "padding:6px 12px; font-size:12px; }}"
            f"QComboBox::drop-down {{ border:none; }}"
            f"QComboBox QAbstractItemView {{ background:{_CARD}; "
            f"color:{_TEXT}; selection-background-color:{_ACCENT}; }}")
        row.addWidget(self._combo)
        row.addStretch()

    def get_key(self) -> str:
        """Return the internal solver key for the selected item."""
        idx = self._combo.currentIndex()
        return _CUSTOM_OPTIONS[idx][1]


# ══════════════════════════════════════════════════════════════════
#  COMPARE RESULTS DIALOG  (shown when "Try All" finishes)
# ══════════════════════════════════════════════════════════════════

class CompareResultsDialog(QDialog):
    """
    Modal dialog displaying the outcome of all matching methods.
    Lets the user pick which result to keep.
    """
    # Emits the internal key of the chosen result
    solver_chosen = pyqtSignal(str)

    def __init__(self, results: dict, parent=None):
        """
        results: { solver_key: (matching|None, report|None, log) }
        """
        super().__init__(parent)
        self.setWindowTitle("Comparison — All Methods")
        self.setMinimumSize(700, 480)
        self.setStyleSheet(
            f"QDialog {{ background:{_BG}; color:{_TEXT}; }}"
            f"QLabel  {{ color:{_TEXT}; background:transparent; }}"
            f"QTextEdit {{ background:{_PANEL}; color:{_TEXT}; "
            f"border:1px solid {_BORDER}; border-radius:6px; "
            "font-family:Consolas,monospace; font-size:11px; }}")

        self._results  = results
        self._chosen   = None
        self._build(results)

    def _build(self, results):
        main = QVBoxLayout(self)
        main.setSpacing(12)
        main.setContentsMargins(20, 18, 20, 16)

        header = QLabel("Results from all matching methods")
        header.setStyleSheet(
            f"font-size:15px; font-weight:700; color:{_ACCENT2};")
        main.addWidget(header)

        # Summary grid
        grid = QGridLayout()
        grid.setSpacing(8)
        headers = ["Method", "Result", "Action"]
        for col, h in enumerate(headers):
            hl = QLabel(h)
            hl.setStyleSheet(
                f"font-size:11px; font-weight:700; color:{_SUBTEXT};")
            grid.addWidget(hl, 0, col)

        # Friendly names for display (no theorem numbers)
        _friendly = {
            'thm4':  "Degree-Capacity Method",
            'thm5':  "Stable Preference Matching",
            'thm6':  "Grade-Priority Sorting",
            'thm7':  "Dataset Enumeration",
            'thm9':  "Exhaustive Search",
            'thm12': "Exchange-Based Matching",
            'thm13': "Resident-Hospital Matching",
        }

        self._use_btns = {}
        for row_i, (key, (matching, report, _log)) in enumerate(
                results.items(), start=1):
            success = matching is not None

            name_lbl = QLabel(_friendly.get(key, key))
            name_lbl.setStyleSheet("font-size:12px;")

            res_lbl = QLabel("✅  Found valid matching" if success
                             else "❌  No valid matching")
            res_lbl.setStyleSheet(
                f"font-size:12px; color:{_GREEN if success else _DANGER};")

            if success:
                use_btn = QPushButton("Use this result")
                use_btn.setStyleSheet(
                    f"QPushButton {{ background:{_ACCENT}; color:#fff; "
                    "border:none; border-radius:6px; padding:5px 14px; "
                    "font-size:11px; font-weight:600; }}"
                    f"QPushButton:hover {{ background:#7c74ff; }}")
                use_btn.clicked.connect(lambda _, k=key: self._choose(k))
                self._use_btns[key] = use_btn
            else:
                use_btn = QLabel("—")
                use_btn.setStyleSheet(f"color:{_SUBTEXT};")

            grid.addWidget(name_lbl, row_i, 0)
            grid.addWidget(res_lbl,  row_i, 1)
            grid.addWidget(use_btn,  row_i, 2)

        grid_w = QWidget()
        grid_w.setStyleSheet(
            f"background:{_CARD}; border-radius:10px; "
            f"border:1px solid {_BORDER}; padding:4px;")
        grid_w.setLayout(grid)
        main.addWidget(grid_w)

        # Log viewer for selected method
        log_lbl = QLabel("Execution log:")
        log_lbl.setStyleSheet(f"font-size:12px; color:{_SUBTEXT};")
        main.addWidget(log_lbl)

        self._log_box = QTextEdit()
        self._log_box.setReadOnly(True)
        self._log_box.setPlaceholderText("Select a method above to view its log…")
        main.addWidget(self._log_box, stretch=1)

        close_btn = QPushButton("Close without changing")
        close_btn.setStyleSheet(
            f"QPushButton {{ background:{_CARD}; color:{_SUBTEXT}; "
            f"border:1px solid {_BORDER}; border-radius:6px; "
            "padding:8px 20px; font-size:12px; }}"
            f"QPushButton:hover {{ color:{_TEXT}; }}")
        close_btn.clicked.connect(self.reject)
        main.addWidget(close_btn, alignment=Qt.AlignRight)

    def _choose(self, key: str):
        self._chosen = key
        self.solver_chosen.emit(key)
        self.accept()

    def get_chosen_key(self):
        return self._chosen


# ══════════════════════════════════════════════════════════════════
#  SMART SELECTION PANEL  (the main exported widget)
# ══════════════════════════════════════════════════════════════════

class SmartSelectionPanel(QWidget):
    """
    Drop-in widget for MEFE Matching GUI.

    Signals:
      strategy_selected(str)  — emitted when user picks a strategy;
                                 str is the resolved internal solver key
                                 (or '__all__' / '__custom__').
    """

    strategy_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._analyzer      : DataAnalyzer | None = None
        self._active_id     : str                 = "auto"
        self._rec_id        : str                 = "auto"
        self._cards         : dict[str, StrategyCard] = {}
        self._solvers_ref   : dict | None         = None   # injected by main

        self._build_ui()

    # ──────────────────────────────────────────────────────────────
    #  UI construction
    # ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        # ── Section header ────────────────────────────────────────
        hdr_row = QHBoxLayout()
        title = QLabel("🎛️   Choose Matching Strategy")
        title.setStyleSheet(
            f"font-size:15px; font-weight:700; color:{_TEXT}; "
            "background:transparent;")
        hdr_row.addWidget(title)
        hdr_row.addStretch()

        hint = QLabel("Upload a file to see smart recommendations")
        hint.setStyleSheet(
            f"font-size:11px; color:{_SUBTEXT}; background:transparent;")
        self._hint_lbl = hint
        hdr_row.addWidget(hint)
        root.addLayout(hdr_row)

        # ── 5 strategy cards  ─────────────────────────────────────
        cards_grid = QGridLayout()
        cards_grid.setSpacing(8)

        # Row 0: Auto, Fast, Accurate
        # Row 1: Compare, Custom  (+ spacer)
        positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]

        for (r, c), strat in zip(positions, STRATEGIES):
            card = StrategyCard(strat)
            card.clicked_signal.connect(self._on_card_clicked)
            self._cards[strat["id"]] = card
            cards_grid.addWidget(card, r, c)

        # Stretch filler so row-1 doesn't look lopsided
        cards_grid.setColumnStretch(2, 1)
        root.addLayout(cards_grid)

        # ── Insight box ───────────────────────────────────────────
        self._insight_box = InsightBox()
        root.addWidget(self._insight_box)

        # ── Description bar ───────────────────────────────────────
        self._desc_bar = DescriptionBar()
        root.addWidget(self._desc_bar)

        # ── Custom selector (only visible when 'custom' picked) ───
        self._custom_row = CustomSelectorRow()
        root.addWidget(self._custom_row)

        # Select "auto" by default
        self._select_card("auto")

    # ──────────────────────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────────────────────
    def set_solvers(self, solvers_dict: dict):
        """
        Inject the THEOREM_SOLVERS dict from main.py.
        Required for 'Try All' mode.
        """
        self._solvers_ref = solvers_dict

    def load_data(self, courses, tas, capacities,
                  ta_utility, course_utility, grade, k):
        """
        Analyse the uploaded dataset and update the panel UI.
        Call this whenever a new Excel file is loaded.
        """
        self._analyzer = DataAnalyzer(
            courses, tas, capacities,
            ta_utility, course_utility, grade, k
        )
        rec_id, reason, insights = self._analyzer.get_recommendation()
        self._rec_id = rec_id

        # Refresh insight box
        chosen_strat = next(s for s in STRATEGIES if s["id"] == rec_id)
        self._insight_box.update(insights, rec_id, reason,
                                 chosen_strat["description"])

        # Update card recommended flags
        for sid, card in self._cards.items():
            card.set_recommended(sid == rec_id)

        # Auto-select the recommended card (but don't override a manual choice)
        self._select_card(rec_id)

        self._hint_lbl.setText(
            f"Analysis complete · {len(courses)} courses · {len(tas)} TAs")

    def get_solver_key(self) -> str:
        """
        Return the internal solver key to pass to THEOREM_SOLVERS.
        Returns '__all__' for compare mode, '__custom__' for custom.
        Resolves 'auto' dynamically if data has been loaded.
        """
        if self._active_id == "compare":
            return "__all__"
        if self._active_id == "custom":
            return self._custom_row.get_key()
        if self._active_id == "auto":
            if self._analyzer:
                return self._analyzer.get_auto_solver_key()
            return "thm4"          # safe default before data loaded
        if self._active_id == "fast":
            return _STRATEGY_FALLBACK.get("fast", "thm6")
        if self._active_id == "accurate":
            # Prefer thm5 unless analyzer says thm13 is better
            if self._analyzer:
                if (self._analyzer.all_positive
                        and self._analyzer.distinct_ta_utils
                        and self._analyzer.distinct_grades):
                    return "thm13"
            return _STRATEGY_FALLBACK.get("accurate", "thm5")
        return "thm4"

    def run_compare(self, solvers_dict, courses, tas, capacities,
                    grade, ta_utility, course_utility, k,
                    parent_widget=None):
        """
        Run every solver and show the comparison dialog.
        Returns the chosen solver key (or None if dialog closed).
        """
        results = {}
        for key, solver_fn in solvers_dict.items():
            try:
                matching, report, log, nc, nt, meta = solver_fn(
                    courses, tas, capacities,
                    grade, ta_utility, course_utility, k
                )
                results[key] = (matching, report, log)
            except Exception as exc:
                results[key] = (None, None, [f"Error: {exc}"])

        dlg = CompareResultsDialog(results, parent_widget or self)
        if dlg.exec_() == QDialog.Accepted:
            return dlg.get_chosen_key()
        return None

    # ──────────────────────────────────────────────────────────────
    #  Internal — card selection handling
    # ──────────────────────────────────────────────────────────────
    def _on_card_clicked(self, sid: str):
        self._select_card(sid)
        # Emit the resolved key so parent can react immediately
        key = self.get_solver_key()
        self.strategy_selected.emit(key)

    def _select_card(self, sid: str):
        self._active_id = sid
        for cid, card in self._cards.items():
            card.set_selected(cid == sid)

        # Show/hide custom selector
        self._custom_row.setVisible(sid == "custom")

        # Update description bar
        strat = next((s for s in STRATEGIES if s["id"] == sid), None)
        if strat:
            self._desc_bar.setText(strat["description"])


# ══════════════════════════════════════════════════════════════════
#  STANDALONE TEST / DEMO
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # ── Dark palette ──────────────────────────────────────────────
    pal = app.palette()
    pal.setColor(pal.Window,        QColor(_BG))
    pal.setColor(pal.WindowText,    QColor(_TEXT))
    pal.setColor(pal.Base,          QColor(_PANEL))
    pal.setColor(pal.AlternateBase, QColor(_CARD))
    pal.setColor(pal.Text,          QColor(_TEXT))
    app.setPalette(pal)

    win = QWidget()
    win.setWindowTitle("Smart Selection Panel — Demo")
    win.resize(900, 560)
    win.setStyleSheet(f"background:{_BG};")

    lay = QVBoxLayout(win)
    lay.setContentsMargins(24, 24, 24, 24)

    panel = SmartSelectionPanel()

    # ── Simulate loading a small dataset ─────────────────────────
    demo_courses    = ["CS101", "CS201"]
    demo_tas        = ["Alice", "Bob", "Charlie", "Dave"]
    demo_capacities = {"CS101": 1, "CS201": 1}
    demo_ta_util    = {
        ("Alice",   "CS101"): 3, ("Alice",   "CS201"): 0,
        ("Bob",     "CS101"): 0, ("Bob",     "CS201"): 2,
        ("Charlie", "CS101"): 1, ("Charlie", "CS201"): 3,
        ("Dave",    "CS101"): 2, ("Dave",    "CS201"): 1,
    }
    demo_cu = {
        ("CS101", "Alice"):   4, ("CS101", "Bob"):     0,
        ("CS101", "Charlie"): 2, ("CS101", "Dave"):    3,
        ("CS201", "Alice"):   0, ("CS201", "Bob"):     3,
        ("CS201", "Charlie"): 4, ("CS201", "Dave"):    2,
    }
    demo_grade = {
        ("Alice",   "CS101"): 9, ("Alice",   "CS201"): 0,
        ("Bob",     "CS101"): 0, ("Bob",     "CS201"): 8,
        ("Charlie", "CS101"): 7, ("Charlie", "CS201"): 9,
        ("Dave",    "CS101"): 8, ("Dave",    "CS201"): 7,
    }

    panel.load_data(
        demo_courses, demo_tas, demo_capacities,
        demo_ta_util, demo_cu, demo_grade, k=2.0
    )

    def on_strategy(key):
        print(f"[Demo] Selected solver key → {key!r}")

    panel.strategy_selected.connect(on_strategy)

    lay.addWidget(panel)
    win.show()
    sys.exit(app.exec_())