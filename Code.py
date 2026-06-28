# =============================================================================
# COMPLETE SMART SELECTION PANEL — Single File Implementation
# TA–Course Matching System with Intelligent Strategy Recommendation
# =============================================================================

import sys
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QFrame, QTextEdit,
    QSplitter, QStatusBar, QMessageBox, QGroupBox, QDialog,
    QSizePolicy, QScrollArea, QToolTip
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QObject, QPoint
from PyQt5.QtGui import QFont, QCursor

# =============================================================================
# SECTION 1: COLOR PALETTE & STYLES
# =============================================================================

COLORS = {
    "green":       "#2ecc71",
    "green_dark":  "#27ae60",
    "green_bg":    "#eafaf1",
    "blue":        "#3498db",
    "blue_dark":   "#2980b9",
    "blue_bg":     "#ebf5fb",
    "yellow":      "#f39c12",
    "yellow_dark": "#e67e22",
    "yellow_bg":   "#fef9e7",
    "red":         "#e74c3c",
    "red_dark":    "#c0392b",
    "red_bg":      "#fdedec",
    "purple":      "#9b59b6",
    "purple_dark": "#8e44ad",
    "purple_bg":   "#f5eef8",
    "gray":        "#95a5a6",
    "gray_bg":     "#f8f9fa",
    "text_dark":   "#2c3e50",
    "text_muted":  "#7f8c8d",
    "white":       "#ffffff",
    "border":      "#dfe6e9",
    "shadow":      "#b2bec3",
}


def get_card_style(color_theme: str, selected: bool, recommended: bool) -> str:
    """
    Returns QSS stylesheet string for a strategy card.
    Visual state changes based on: selected, recommended, or normal.
    """
    c      = COLORS.get(color_theme,            COLORS["blue"])
    c_bg   = COLORS.get(f"{color_theme}_bg",    COLORS["gray_bg"])

    if selected:
        # Solid colored border + tinted background = clearly chosen
        return f"""
            QFrame#strategyCard {{
                background-color: {c_bg};
                border: 2.5px solid {c};
                border-radius: 12px;
                padding: 4px;
            }}
        """
    elif recommended:
        # Dashed border = "we suggest this one"
        return f"""
            QFrame#strategyCard {{
                background-color: {COLORS['white']};
                border: 2px dashed {c};
                border-radius: 12px;
                padding: 4px;
            }}
            QFrame#strategyCard:hover {{
                background-color: {c_bg};
                border: 2px solid {c};
            }}
        """
    else:
        # Default neutral card
        return f"""
            QFrame#strategyCard {{
                background-color: {COLORS['white']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 12px;
                padding: 4px;
            }}
            QFrame#strategyCard:hover {{
                background-color: {c_bg};
                border: 1.5px solid {c};
            }}
        """


# ---------- Static QSS blocks ------------------------------------------------

PANEL_STYLE = f"""
    QGroupBox {{
        font-size: 14px;
        font-weight: bold;
        color: {COLORS['text_dark']};
        border: 2px solid {COLORS['border']};
        border-radius: 10px;
        margin-top: 12px;
        padding-top: 8px;
        background-color: {COLORS['white']};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 8px;
        background-color: {COLORS['white']};
        color: {COLORS['text_dark']};
    }}
"""

INSIGHT_BANNER_STYLE = f"""
    QFrame {{
        background-color: #eaf4fb;
        border: 1px solid #aed6f1;
        border-radius: 8px;
        padding: 6px;
    }}
    QLabel {{
        color: {COLORS['text_dark']};
        font-size: 12px;
    }}
"""

BADGE_STYLES = {
    "RECOMMENDED": f"""
        QLabel {{
            background-color: {COLORS['green']};
            color: white;
            border-radius: 8px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: bold;
        }}
    """,
    "EXPERIMENTAL": f"""
        QLabel {{
            background-color: {COLORS['yellow']};
            color: white;
            border-radius: 8px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: bold;
        }}
    """,
    "ADVANCED": f"""
        QLabel {{
            background-color: {COLORS['purple']};
            color: white;
            border-radius: 8px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: bold;
        }}
    """,
}

EXPLANATION_STYLE = f"""
    QFrame {{
        background-color: {COLORS['gray_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
    }}
    QLabel {{
        color: {COLORS['text_dark']};
        font-size: 12px;
        padding: 4px;
    }}
"""

WHY_BUTTON_STYLE = f"""
    QPushButton {{
        color: {COLORS['blue']};
        background: transparent;
        border: none;
        font-size: 12px;
        text-decoration: underline;
        text-align: left;
        padding: 0px;
    }}
    QPushButton:hover {{
        color: {COLORS['blue_dark']};
    }}
"""

RUN_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['green']};
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 13px;
        font-weight: bold;
        padding: 10px 24px;
        min-height: 36px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['green_dark']};
    }}
    QPushButton:disabled {{
        background-color: {COLORS['gray']};
        color: #ecf0f1;
    }}
"""

WARNING_STYLE = f"""
    QLabel {{
        color: {COLORS['yellow_dark']};
        background-color: {COLORS['yellow_bg']};
        border: 1px solid {COLORS['yellow']};
        border-radius: 6px;
        padding: 6px;
        font-size: 11px;
    }}
"""


# =============================================================================
# SECTION 2: STRATEGY CONFIGURATION
# =============================================================================

@dataclass
class Strategy:
    """
    A single matching strategy as presented to the user.
    The backend_key field is the only connection to the actual algorithm
    and is never shown in the UI.
    """
    id:                   str
    label:                str
    icon:                 str
    short_desc:           str
    tooltip:              str
    detailed_explanation: str
    why_explanation:      str
    backend_key:          str            # Hidden from user — maps to algorithm
    color_theme:          str
    badge:                Optional[str] = None
    warning:              Optional[str] = None
    conditions:           List[str]      = field(default_factory=list)


# ---------- All five strategies ----------------------------------------------

STRATEGIES = [
    Strategy(
        id="auto",
        label="Auto Select Best Method",
        icon="✅",
        short_desc="Let the system pick the best approach for your data",
        tooltip=(
            "Auto Select: The system examines your uploaded data — "
            "number of TAs, courses, and preferences — then picks "
            "the most suitable method automatically. Perfect if you're unsure."
        ),
        detailed_explanation=(
            "The system will analyze your data and automatically choose "
            "the most effective matching method. You don't need to know "
            "anything technical — just upload your file and click Run."
        ),
        why_explanation=(
            "We recommend this when you're unsure about your data size or "
            "structure. The system checks:\n"
            "  • How many TAs and courses you have\n"
            "  • How many preferences each TA listed\n"
            "  • Whether capacities are uniform or varied\n\n"
            "Then it silently picks the best algorithm for you."
        ),
        backend_key="auto",
        color_theme="green",
        badge="RECOMMENDED",
        conditions=["default", "unknown_structure", "mixed"],
    ),
    Strategy(
        id="fast",
        label="Fast Matching",
        icon="⚡",
        short_desc="Quick results — ideal for large datasets",
        tooltip=(
            "Fast Matching: Designed for speed. Works best when TAs have "
            "a small number of course preferences (1–2 choices each). "
            "Great for large groups of TAs."
        ),
        detailed_explanation=(
            "This method processes your data very quickly. It's best when "
            "each TA has listed only one or two preferred courses. "
            "Results are produced in seconds even with hundreds of TAs."
        ),
        why_explanation=(
            "Fast Matching works well because:\n"
            "  • Each TA has very few preferences (≤ 2 courses)\n"
            "  • The matching problem is simpler to solve\n"
            "  • No complex comparisons are needed\n\n"
            "Trade-off: May not find the absolute best match in complex "
            "cases, but is significantly faster."
        ),
        backend_key="fast_matching",
        color_theme="blue",
        badge=None,
        conditions=["low_degree", "large_dataset", "uniform_capacity_1"],
        warning=None,
    ),
    Strategy(
        id="accurate",
        label="High Accuracy Matching",
        icon="🎯",
        short_desc="Best quality matches — takes a bit longer",
        tooltip=(
            "High Accuracy: Finds the most stable and fair assignments. "
            "Uses a thorough approach that considers everyone's preferences. "
            "Best for smaller datasets or when quality matters most."
        ),
        detailed_explanation=(
            "This method carefully evaluates all preferences to find the "
            "most stable set of matches — meaning no TA would prefer to "
            "switch to a different course and no course would prefer a "
            "different TA. Ideal when fairness and quality are the priority."
        ),
        why_explanation=(
            "High Accuracy is recommended because:\n"
            "  • Your dataset is small enough to handle thorough analysis\n"
            "  • TAs have multiple course preferences listed\n"
            "  • Course capacities vary (not all the same)\n\n"
            "This method guarantees stable, fair outcomes but may take "
            "slightly longer on very large datasets."
        ),
        backend_key="stable_matching",
        color_theme="green",
        badge=None,
        conditions=["small_dataset", "high_degree", "varied_capacity"],
    ),
    Strategy(
        id="compare",
        label="Try All Methods",
        icon="🔍",
        short_desc="Run everything and compare results side-by-side",
        tooltip=(
            "Try All Methods: Runs every available matching approach on "
            "your data and shows you the results from each. Useful when "
            "you want to see which method gives the best outcome."
        ),
        detailed_explanation=(
            "All available matching methods will run on your data. "
            "Results from each method are displayed together so you can "
            "compare and choose the best outcome. "
            "Note: This takes longer than running a single method."
        ),
        why_explanation=(
            "Use this option when:\n"
            "  • You want to validate results across methods\n"
            "  • You're exploring which approach fits your organisation\n"
            "  • You need to justify your matching decisions\n\n"
            "⚠️ This runs multiple processes — expect it to take more time."
        ),
        backend_key="run_all",
        color_theme="yellow",
        badge="EXPERIMENTAL",
        conditions=["validation_needed", "small_dataset"],
        warning="This may take significantly longer for large datasets.",
    ),
    Strategy(
        id="custom",
        label="Custom Selection",
        icon="🧪",
        short_desc="Advanced: manually choose your matching approach",
        tooltip=(
            "Custom Selection: For advanced users who want control. "
            "You'll be shown a set of matching options with descriptions "
            "so you can manually pick one."
        ),
        detailed_explanation=(
            "You'll be presented with all available matching options. "
            "Each option includes a plain-English description to guide "
            "your choice. Use this if you have specific requirements "
            "or want to experiment."
        ),
        why_explanation=(
            "Custom Selection gives you full control:\n"
            "  • Choose any matching approach manually\n"
            "  • Useful for research or testing purposes\n"
            "  • You can override the system's recommendation\n\n"
            "⚠️ Recommended only if you understand the differences "
            "between matching approaches."
        ),
        backend_key="custom",
        color_theme="purple",
        badge="ADVANCED",
        conditions=["user_override"],
        warning="Best used when you have specific requirements in mind.",
    ),
]

# Quick lookup dictionary: strategy_id → Strategy object
STRATEGY_MAP = {s.id: s for s in STRATEGIES}


# =============================================================================
# SECTION 3: DATA ANALYZER
# =============================================================================

@dataclass
class DataProfile:
    """
    All computed statistics about the uploaded dataset.
    Drives the recommendation engine — never shown to the user.
    """
    num_tas:                int   = 0
    num_courses:            int   = 0
    avg_ta_degree:          float = 0.0   # Avg course preferences per TA
    max_ta_degree:          int   = 0
    min_ta_degree:          int   = 0
    avg_capacity:           float = 0.0
    max_capacity:           int   = 0
    min_capacity:           int   = 0
    all_capacity_one:       bool  = False  # Every course has capacity = 1
    uniform_capacity:       bool  = False  # All capacities identical
    total_preference_edges: int   = 0      # Total (TA, course) pairs in file
    has_utility_scores:     bool  = False  # Utility/weight column present
    is_small:               bool  = False
    is_large:               bool  = False
    sparsity:               float = 0.0   # Fraction of possible edges present


@dataclass
class AnalysisResult:
    """
    Output produced by DataAnalyzer after examining the uploaded file.
    Contains the recommendation + human-readable insight messages.
    """
    recommended_strategy_id: str
    confidence:              float                        # 0.0 – 1.0
    insights:                List[Tuple[str, str]] = field(default_factory=list)
    warnings:                List[str]             = field(default_factory=list)
    profile:                 Optional[DataProfile] = None


class DataAnalyzer:
    """
    Analyzes a pandas DataFrame and recommends a matching strategy.

    Expected DataFrame columns (flexible column-name matching):
      ta_id / ta / teaching_assistant  → TA identifiers
      course_id / course / subject     → Course identifiers
      capacity / cap / seats           → Course capacity  (optional)
      utility / weight / score         → Preference score (optional)
    """

    # ── Thresholds (tune to match backend performance characteristics) ────
    SMALL_DATASET_THRESHOLD = 500     # num_tas × num_courses
    LARGE_DATASET_THRESHOLD = 5000
    LOW_DEGREE_THRESHOLD    = 2       # Avg preferences per TA
    HIGH_DEGREE_THRESHOLD   = 5

    def __init__(self):
        self._profile: Optional[DataProfile] = None

    # ── Public entry point ────────────────────────────────────────────────

    def analyze(self, df: pd.DataFrame) -> AnalysisResult:
        """
        Analyze the DataFrame and return a recommendation with insights.
        Safe: any exception falls back to 'auto'.
        """
        try:
            profile                = self._build_profile(df)
            self._profile          = profile
            recommendation, conf   = self._recommend(profile)
            insights               = self._generate_insights(profile, recommendation)
            warnings               = self._generate_warnings(profile, recommendation)

            return AnalysisResult(
                recommended_strategy_id = recommendation,
                confidence              = conf,
                insights                = insights,
                warnings                = warnings,
                profile                 = profile,
            )
        except Exception as exc:
            return AnalysisResult(
                recommended_strategy_id = "auto",
                confidence              = 0.5,
                insights = [(
                    "ℹ️",
                    f"Could not fully analyse data: {exc}. "
                    "Auto Select will handle it safely."
                )],
                warnings = [],
                profile  = None,
            )

    # ── Profile builder ───────────────────────────────────────────────────

    def _build_profile(self, df: pd.DataFrame) -> DataProfile:
        p = DataProfile()

        ta_col       = self._find_col(df, ["ta_id","ta","teaching_assistant","tutor","applicant"])
        course_col   = self._find_col(df, ["course_id","course","subject","class","module"])
        capacity_col = self._find_col(df, ["capacity","cap","seats","slots","max"])
        utility_col  = self._find_col(df, ["utility","weight","score","preference","rating","value"])

        if ta_col is None or course_col is None:
            raise ValueError("Could not identify TA and Course columns in the file.")

        # Basic counts
        p.num_tas               = df[ta_col].nunique()
        p.num_courses           = df[course_col].nunique()
        p.total_preference_edges= len(df)
        p.has_utility_scores    = utility_col is not None

        # TA degree
        ta_degree       = df.groupby(ta_col)[course_col].count()
        p.avg_ta_degree = float(ta_degree.mean())
        p.max_ta_degree = int(ta_degree.max())
        p.min_ta_degree = int(ta_degree.min())

        # Capacity
        if capacity_col is not None:
            caps            = df.groupby(course_col)[capacity_col].first()
            p.avg_capacity  = float(caps.mean())
            p.max_capacity  = int(caps.max())
            p.min_capacity  = int(caps.min())
        else:
            p.avg_capacity  = 1.0
            p.max_capacity  = 1
            p.min_capacity  = 1

        p.all_capacity_one  = (p.min_capacity == 1 and p.max_capacity == 1)
        p.uniform_capacity  = (p.min_capacity == p.max_capacity)

        # Size
        size_score  = p.num_tas * p.num_courses
        p.is_small  = size_score < self.SMALL_DATASET_THRESHOLD
        p.is_large  = size_score > self.LARGE_DATASET_THRESHOLD

        # Sparsity
        max_possible = p.num_tas * p.num_courses
        p.sparsity   = (1.0 - p.total_preference_edges / max_possible
                        if max_possible > 0 else 0.0)
        return p

    # ── Recommendation rules ──────────────────────────────────────────────

    def _recommend(self, p: DataProfile) -> Tuple[str, float]:
        """
        Priority-ordered rule table.
        Returns (strategy_id, confidence).
        """
        # Rule 1: Small + many preferences → thorough matching worthwhile
        if p.is_small and p.avg_ta_degree >= self.HIGH_DEGREE_THRESHOLD:
            return "accurate", 0.92

        # Rule 2: Low degree (≤2 preferences per TA) → fast matching ideal
        if p.avg_ta_degree <= self.LOW_DEGREE_THRESHOLD:
            return ("fast", 0.95) if p.all_capacity_one else ("fast", 0.85)

        # Rule 3: All capacity = 1, small → thorough matching
        if p.all_capacity_one and p.is_small:
            return "accurate", 0.88

        # Rule 4: Large dataset → speed is paramount
        if p.is_large:
            return "fast", 0.80

        # Rule 5: Small + varied capacity → thorough matching
        if p.is_small and not p.uniform_capacity:
            return "accurate", 0.85

        # Default: let the backend decide
        return "auto", 0.70

    # ── Insight generation ────────────────────────────────────────────────

    def _generate_insights(
        self, p: DataProfile, rec_id: str
    ) -> List[Tuple[str, str]]:
        insights = []

        # Dataset size
        if p.is_small:
            insights.append(("💡",
                f"Your dataset is small ({p.num_tas} TAs, {p.num_courses} courses) "
                "→ High Accuracy Matching is fast enough and gives the best results."
            ))
        elif p.is_large:
            insights.append(("💡",
                f"You have a large dataset ({p.num_tas} TAs, {p.num_courses} courses) "
                "→ Fast Matching is recommended to keep processing time short."
            ))
        else:
            insights.append(("📊",
                f"Medium-sized dataset detected: {p.num_tas} TAs across "
                f"{p.num_courses} courses."
            ))

        # TA preference degree
        if p.avg_ta_degree <= 1.5:
            insights.append(("💡",
                f"Each TA listed only ~{p.avg_ta_degree:.1f} course preference(s) "
                "→ Fast Matching will work perfectly."
            ))
        elif p.avg_ta_degree >= self.HIGH_DEGREE_THRESHOLD:
            insights.append(("💡",
                f"TAs have many preferences ({p.avg_ta_degree:.1f} courses each on average) "
                "→ High Accuracy Matching will find the best overall assignments."
            ))
        else:
            insights.append(("📋",
                f"TAs listed an average of {p.avg_ta_degree:.1f} course preferences each."
            ))

        # Capacity
        if p.all_capacity_one:
            insights.append(("💡",
                "All courses have capacity 1 (one TA per course) "
                "→ The matching problem is well-defined and any method works well."
            ))
        elif not p.uniform_capacity:
            insights.append(("💡",
                f"Course capacities vary ({p.min_capacity}–{p.max_capacity} TAs per course) "
                "→ High Accuracy Matching handles this best."
            ))

        # Utility scores
        if p.has_utility_scores:
            insights.append(("⭐",
                "Preference scores detected in your file "
                "→ These will be used to optimise match quality."
            ))

        return insights

    def _generate_warnings(
        self, p: DataProfile, rec_id: str
    ) -> List[str]:
        warnings = []
        if p.num_tas == 0 or p.num_courses == 0:
            warnings.append("⚠️ No TAs or courses detected. Please check your file format.")
        if rec_id == "compare" and p.is_large:
            warnings.append("⚠️ Running all methods on a large dataset may take several minutes.")
        if p.max_ta_degree == 0:
            warnings.append("⚠️ Some TAs have no preferences listed. They may not be matched.")
        return warnings

    # ── Utility ───────────────────────────────────────────────────────────

    @staticmethod
    def _find_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
        """Case-insensitive column finder."""
        lower = {c.lower(): c for c in df.columns}
        for cand in candidates:
            if cand.lower() in lower:
                return lower[cand.lower()]
        return None


# =============================================================================
# SECTION 4: BACKGROUND ANALYSIS WORKER
# =============================================================================

class AnalysisWorker(QObject):
    """
    Runs DataAnalyzer in a QThread so the GUI stays responsive.
    """
    finished = pyqtSignal(object)   # AnalysisResult
    error    = pyqtSignal(str)

    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self._df = df

    @pyqtSlot()
    def run(self):
        try:
            result = DataAnalyzer().analyze(self._df)
            self.finished.emit(result)
        except Exception as exc:
            self.error.emit(str(exc))


# =============================================================================
# SECTION 5: "WHY THIS?" DIALOG
# =============================================================================

class WhyDialog(QDialog):
    """
    Modal dialog explaining the reasoning behind a strategy recommendation.
    Uses plain English — no algorithm names.
    """
    def __init__(self, strategy: Strategy, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Why this recommendation?")
        self.setMinimumSize(420, 300)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel(f"{strategy.icon}  {strategy.label}")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(title)

        # Separator line
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {COLORS['border']};")
        layout.addWidget(sep)

        # Explanation body
        body = QTextEdit()
        body.setReadOnly(True)
        body.setPlainText(strategy.why_explanation)
        body.setFont(QFont("Segoe UI", 11))
        body.setStyleSheet(f"""
            QTextEdit {{
                border: none;
                background: transparent;
                color: {COLORS['text_dark']};
            }}
        """)
        layout.addWidget(body)

        # Close button
        close_btn = QPushButton("Got it  ✓")
        close_btn.setStyleSheet(RUN_BUTTON_STYLE)
        close_btn.clicked.connect(self.accept)
        close_btn.setFixedWidth(120)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)


# =============================================================================
# SECTION 6: CUSTOM SELECTION SUB-PANEL
# =============================================================================

class CustomSelectionPanel(QWidget):
    """
    Shown only when the user picks 'Custom Selection'.
    Presents plain-English sub-options without exposing algorithm names.
    """
    backend_key_selected = pyqtSignal(str)

    # (display label, backend key, tooltip description)
    CUSTOM_OPTIONS = [
        (
            "One-to-one assignment  (each TA gets one course)",
            "stable_matching",
            "Best when each TA should be matched to exactly one course."
        ),
        (
            "Multi-slot assignment  (TAs can cover multiple courses)",
            "fast_matching",
            "Use when a single TA can be assigned to several courses."
        ),
        (
            "Priority-based assignment  (use preference scores)",
            "weighted_matching",
            "Best when your file includes preference ratings or scores."
        ),
        (
            "Balanced assignment  (distribute TAs evenly)",
            "balanced_matching",
            "Tries to spread TA workload as evenly as possible."
        ),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        header = QLabel("Select the assignment type that fits your needs:")
        header.setFont(QFont("Segoe UI", 11))
        header.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(header)

        for label, key, desc in self.CUSTOM_OPTIONS:
            btn = QPushButton(f"  {label}")
            btn.setToolTip(desc)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setMinimumHeight(36)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS['white']};
                    border: 1.5px solid {COLORS['border']};
                    border-radius: 6px;
                    color: {COLORS['text_dark']};
                    font-size: 11px;
                    text-align: left;
                    padding-left: 10px;
                }}
                QPushButton:checked {{
                    background: {COLORS['purple_bg']};
                    border: 2px solid {COLORS['purple']};
                    color: {COLORS['purple_dark']};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: {COLORS['purple_bg']};
                }}
            """)
            btn.clicked.connect(
                lambda _checked, k=key: self.backend_key_selected.emit(k)
            )
            layout.addWidget(btn)


# =============================================================================
# SECTION 7: STRATEGY CARD WIDGET
# =============================================================================

class StrategyCard(QFrame):
    """
    A single clickable card representing one matching strategy.

    Signals:
        clicked(strategy_id)   — user clicked the card
        why_clicked(strategy_id) — user clicked "Why this?"
    """
    clicked      = pyqtSignal(str)
    why_clicked  = pyqtSignal(str)

    def __init__(
        self,
        strategy:       Strategy,
        is_recommended: bool = False,
        parent=None
    ):
        super().__init__(parent)
        self.strategy       = strategy
        self.is_recommended = is_recommended
        self._selected      = False

        self.setObjectName("strategyCard")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setToolTip(strategy.tooltip)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setMinimumHeight(90)

        self._build_ui()
        self._apply_style()

    # ── Layout ────────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        # Row 1: icon + name + badge
        top = QHBoxLayout()
        top.setSpacing(8)

        icon_lbl = QLabel(self.strategy.icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 18))
        icon_lbl.setFixedWidth(32)
        icon_lbl.setAlignment(Qt.AlignCenter)
        top.addWidget(icon_lbl)

        name_lbl = QLabel(self.strategy.label)
        name_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        name_lbl.setStyleSheet(
            f"color: {COLORS['text_dark']}; background: transparent;"
        )
        top.addWidget(name_lbl, stretch=1)

        if self.strategy.badge:
            badge = QLabel(self.strategy.badge)
            badge.setStyleSheet(BADGE_STYLES.get(self.strategy.badge, ""))
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedHeight(20)
            top.addWidget(badge)

        layout.addLayout(top)

        # Row 2: short description
        desc = QLabel(self.strategy.short_desc)
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(
            f"color: {COLORS['text_muted']}; background: transparent;"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Row 3: "Why this?" link
        bottom = QHBoxLayout()
        bottom.addStretch()

        self.why_btn = QPushButton("Why this recommendation? →")
        self.why_btn.setStyleSheet(WHY_BUTTON_STYLE)
        self.why_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.why_btn.setVisible(self.is_recommended)
        self.why_btn.clicked.connect(
            lambda: self.why_clicked.emit(self.strategy.id)
        )
        bottom.addWidget(self.why_btn)
        layout.addLayout(bottom)

    # ── State management ──────────────────────────────────────────────────

    def set_selected(self, selected: bool):
        self._selected = selected
        self.why_btn.setVisible(selected or self.is_recommended)
        self._apply_style()

    def set_recommended(self, recommended: bool):
        self.is_recommended = recommended
        self.why_btn.setVisible(self._selected or recommended)
        self._apply_style()

    def is_selected(self) -> bool:
        return self._selected

    # ── Styling ───────────────────────────────────────────────────────────

    def _apply_style(self):
        self.setStyleSheet(
            get_card_style(
                self.strategy.color_theme,
                self._selected,
                self.is_recommended
            )
        )

    # ── Mouse events ──────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.strategy.id)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        QToolTip.showText(
            self.mapToGlobal(QPoint(0, self.height())),
            self.strategy.tooltip,
            self
        )
        super().enterEvent(event)


# =============================================================================
# SECTION 8: SMART SELECTION PANEL (main widget)
# =============================================================================

class SmartSelectionPanel(QWidget):
    """
    The complete 'Choose Matching Strategy' panel.

    Drop into any QLayout. Workflow:
      1. Call load_dataframe(df) after the user uploads a file.
      2. Panel auto-analyses data, highlights recommendation.
      3. User reviews cards and clicks 'Run Matching'.
      4. strategy_selected(backend_key) is emitted.

    Signals:
        strategy_selected(backend_key: str)
    """
    strategy_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_strategy_id:  Optional[str]         = None
        self._current_backend_key:  Optional[str]         = None
        self._analysis_result:      Optional[AnalysisResult] = None
        self._cards:                dict                  = {}
        self._analysis_thread:      Optional[QThread]     = None
        self._custom_backend_key:   Optional[str]         = None

        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Outer group box
        group = QGroupBox("   Choose Matching Strategy")
        group.setStyleSheet(PANEL_STYLE)
        group.setFont(QFont("Segoe UI", 13, QFont.Bold))

        inner = QVBoxLayout(group)
        inner.setContentsMargins(16, 16, 16, 16)
        inner.setSpacing(12)

        # 1. Insight banner (hidden until file loaded)
        self._insight_frame = self._build_insight_banner()
        inner.addWidget(self._insight_frame)

        # 2. Prompt label
        prompt = QLabel("Select how you want the matching to be done:")
        prompt.setFont(QFont("Segoe UI", 11))
        prompt.setStyleSheet(f"color: {COLORS['text_muted']};")
        inner.addWidget(prompt)

        # 3. Strategy cards (two rows)
        self._cards_container = self._build_cards_grid()
        inner.addWidget(self._cards_container)

        # 4. Custom sub-panel (hidden until 'Custom' chosen)
        self._custom_panel = CustomSelectionPanel()
        self._custom_panel.setVisible(False)
        self._custom_panel.backend_key_selected.connect(
            self._on_custom_backend_selected
        )
        inner.addWidget(self._custom_panel)

        # 5. Explanation panel (hidden until card selected)
        self._explanation_frame = self._build_explanation_panel()
        inner.addWidget(self._explanation_frame)

        # 6. Warning label
        self._warning_label = QLabel()
        self._warning_label.setWordWrap(True)
        self._warning_label.setStyleSheet(WARNING_STYLE)
        self._warning_label.setVisible(False)
        inner.addWidget(self._warning_label)

        # 7. Run button (right-aligned)
        run_row = QHBoxLayout()
        run_row.addStretch()
        self._run_btn = QPushButton("▶  Run Matching")
        self._run_btn.setStyleSheet(RUN_BUTTON_STYLE)
        self._run_btn.setEnabled(False)
        self._run_btn.setToolTip(
            "Select a strategy above, then click here to run."
        )
        self._run_btn.clicked.connect(self._on_run_clicked)
        run_row.addWidget(self._run_btn)
        inner.addLayout(run_row)

        root.addWidget(group)

    def _build_insight_banner(self) -> QFrame:
        """Blue banner that shows auto-analysis results after file upload."""
        frame = QFrame()
        frame.setStyleSheet(INSIGHT_BANNER_STYLE)
        frame.setVisible(False)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # Header row
        header_row = QHBoxLayout()

        hdr_icon = QLabel("🔎")
        hdr_icon.setFont(QFont("Segoe UI Emoji", 13))
        header_row.addWidget(hdr_icon)

        self._insight_header = QLabel("Analysing your data...")
        self._insight_header.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self._insight_header.setStyleSheet(f"color: {COLORS['blue_dark']};")
        header_row.addWidget(self._insight_header, stretch=1)

        self._loading_label = QLabel("⏳ Please wait...")
        self._loading_label.setFont(QFont("Segoe UI", 10))
        self._loading_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        header_row.addWidget(self._loading_label)

        layout.addLayout(header_row)

        # Container for insight bullet rows
        self._insights_container = QVBoxLayout()
        self._insights_container.setSpacing(3)
        layout.addLayout(self._insights_container)

        return frame

    def _build_cards_grid(self) -> QWidget:
        """Two-row grid: [Auto | Fast | Accurate] / [Compare | Custom]."""
        container = QWidget()
        outer = QVBoxLayout(container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        # Row 1
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        for sid in ["auto", "fast", "accurate"]:
            card = StrategyCard(STRATEGY_MAP[sid], is_recommended=False)
            card.clicked.connect(self._on_card_clicked)
            card.why_clicked.connect(self._show_why_dialog)
            self._cards[sid] = card
            row1.addWidget(card)
        outer.addLayout(row1)

        # Row 2
        row2 = QHBoxLayout()
        row2.setSpacing(8)
        for sid in ["compare", "custom"]:
            card = StrategyCard(STRATEGY_MAP[sid], is_recommended=False)
            card.clicked.connect(self._on_card_clicked)
            card.why_clicked.connect(self._show_why_dialog)
            self._cards[sid] = card
            row2.addWidget(card)
        row2.addStretch()
        outer.addLayout(row2)

        return container

    def _build_explanation_panel(self) -> QFrame:
        """Grey panel that explains the currently selected strategy."""
        frame = QFrame()
        frame.setStyleSheet(EXPLANATION_STYLE)
        frame.setVisible(False)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)

        title_row = QHBoxLayout()
        self._exp_icon  = QLabel()
        self._exp_icon.setFont(QFont("Segoe UI Emoji", 16))
        title_row.addWidget(self._exp_icon)

        self._exp_title = QLabel()
        self._exp_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self._exp_title.setStyleSheet(f"color: {COLORS['text_dark']};")
        title_row.addWidget(self._exp_title, stretch=1)
        layout.addLayout(title_row)

        self._exp_text = QLabel()
        self._exp_text.setFont(QFont("Segoe UI", 10))
        self._exp_text.setStyleSheet(f"color: {COLORS['text_dark']};")
        self._exp_text.setWordWrap(True)
        layout.addWidget(self._exp_text)

        return frame

    # ── Public API ────────────────────────────────────────────────────────

    def load_dataframe(self, df: pd.DataFrame):
        """
        Call this immediately after the user uploads a file.
        Starts background analysis and updates the UI with recommendations.
        """
        self._insight_frame.setVisible(True)
        self._insight_header.setText("Analysing your data...")
        self._loading_label.setVisible(True)
        self._clear_insights()

        # Spin up background thread
        self._analysis_thread = QThread()
        self._worker = AnalysisWorker(df)
        self._worker.moveToThread(self._analysis_thread)

        self._analysis_thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_analysis_complete)
        self._worker.error.connect(self._on_analysis_error)
        self._worker.finished.connect(self._analysis_thread.quit)
        self._worker.error.connect(self._analysis_thread.quit)

        self._analysis_thread.start()

    def get_selected_backend_key(self) -> Optional[str]:
        """Return the backend algorithm key for the selected strategy."""
        return self._current_backend_key

    def get_selected_strategy_id(self) -> Optional[str]:
        """Return the user-facing strategy ID."""
        return self._current_strategy_id

    def reset(self):
        """Reset panel to initial blank state."""
        self._current_strategy_id = None
        self._current_backend_key = None
        self._analysis_result     = None

        for card in self._cards.values():
            card.set_selected(False)
            card.set_recommended(False)

        self._insight_frame.setVisible(False)
        self._explanation_frame.setVisible(False)
        self._warning_label.setVisible(False)
        self._custom_panel.setVisible(False)
        self._run_btn.setEnabled(False)
        self._clear_insights()

    # ── Slots ─────────────────────────────────────────────────────────────

    @pyqtSlot(object)
    def _on_analysis_complete(self, result: AnalysisResult):
        self._analysis_result = result
        self._loading_label.setVisible(False)

        pct = int(result.confidence * 100)
        self._insight_header.setText(
            f"📊 Data Analysis Complete  ({pct}% confidence)"
        )

        # Populate insight rows
        self._clear_insights()
        for icon, message in result.insights:
            row = QHBoxLayout()
            row.setSpacing(6)

            i_lbl = QLabel(icon)
            i_lbl.setFont(QFont("Segoe UI Emoji", 11))
            i_lbl.setFixedWidth(24)
            i_lbl.setAlignment(Qt.AlignTop)
            row.addWidget(i_lbl)

            m_lbl = QLabel(message)
            m_lbl.setFont(QFont("Segoe UI", 10))
            m_lbl.setStyleSheet(f"color: {COLORS['text_dark']};")
            m_lbl.setWordWrap(True)
            row.addWidget(m_lbl, stretch=1)

            self._insights_container.addLayout(row)

        # Highlight recommended card and auto-select it
        rec_id = result.recommended_strategy_id
        for sid, card in self._cards.items():
            card.set_recommended(sid == rec_id)

        self._select_strategy(rec_id)

    @pyqtSlot(str)
    def _on_analysis_error(self, error_msg: str):
        self._loading_label.setVisible(False)
        self._insight_header.setText("⚠️ Could not fully analyse file — using safe default")
        self._select_strategy("auto")

    @pyqtSlot(str)
    def _on_card_clicked(self, strategy_id: str):
        self._select_strategy(strategy_id)

    @pyqtSlot(str)
    def _show_why_dialog(self, strategy_id: str):
        strategy = STRATEGY_MAP.get(strategy_id)
        if strategy:
            WhyDialog(strategy, parent=self).exec_()

    @pyqtSlot(str)
    def _on_custom_backend_selected(self, backend_key: str):
        self._custom_backend_key  = backend_key
        self._current_backend_key = backend_key
        self._run_btn.setEnabled(True)

    def _on_run_clicked(self):
        if self._current_backend_key:
            self.strategy_selected.emit(self._current_backend_key)

    # ── Internal helpers ──────────────────────────────────────────────────

    def _select_strategy(self, strategy_id: str):
        """Update all visual elements for the newly chosen strategy."""
        if strategy_id not in STRATEGY_MAP:
            return

        strategy = STRATEGY_MAP[strategy_id]
        self._current_strategy_id = strategy_id

        # Card states
        for sid, card in self._cards.items():
            card.set_selected(sid == strategy_id)

        # Show/hide custom sub-panel
        is_custom = strategy_id == "custom"
        self._custom_panel.setVisible(is_custom)

        # Resolve backend key
        if strategy_id == "auto" and self._analysis_result:
            rec_id = self._analysis_result.recommended_strategy_id
            if rec_id in STRATEGY_MAP and rec_id != "auto":
                self._current_backend_key = STRATEGY_MAP[rec_id].backend_key
            else:
                self._current_backend_key = strategy.backend_key
        elif is_custom:
            self._current_backend_key = None   # Wait for sub-selection
        else:
            self._current_backend_key = strategy.backend_key

        # Explanation panel
        self._exp_icon.setText(strategy.icon)
        self._exp_title.setText(strategy.label)
        self._exp_text.setText(strategy.detailed_explanation)
        self._explanation_frame.setVisible(True)

        # Warning
        if strategy.warning:
            self._warning_label.setText(f"⚠️  {strategy.warning}")
            self._warning_label.setVisible(True)
        else:
            self._warning_label.setVisible(False)

        # Enable Run only when we have a concrete key
        self._run_btn.setEnabled(self._current_backend_key is not None)

    def _clear_insights(self):
        """Remove all rows from the insights container."""
        while self._insights_container.count():
            item = self._insights_container.takeAt(0)
            if item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()


# =============================================================================
# SECTION 9: FAKE BACKEND FUNCTIONS (replace with your real algorithms)
# =============================================================================

def run_auto_matching(df: pd.DataFrame) -> dict:
    """Placeholder: internally picks the best algorithm."""
    return {"method": "auto", "matched_pairs": len(df), "status": "success"}

def run_fast_matching(df: pd.DataFrame) -> dict:
    """Placeholder: fast matching algorithm."""
    return {"method": "fast_matching", "matched_pairs": len(df), "status": "success"}

def run_stable_matching(df: pd.DataFrame) -> dict:
    """Placeholder: stable / high-accuracy matching."""
    return {"method": "stable_matching", "matched_pairs": len(df), "status": "success"}

def run_all_methods(df: pd.DataFrame) -> dict:
    """Placeholder: runs all methods and collects results."""
    return {
        "method": "run_all",
        "results": {
            "fast":   run_fast_matching(df),
            "stable": run_stable_matching(df),
        },
        "status": "success",
    }

def run_weighted_matching(df: pd.DataFrame) -> dict:
    return {"method": "weighted_matching", "matched_pairs": len(df), "status": "success"}

def run_balanced_matching(df: pd.DataFrame) -> dict:
    return {"method": "balanced_matching", "matched_pairs": len(df), "status": "success"}


# Maps backend key → actual function
BACKEND_FUNCTIONS = {
    "auto":              run_auto_matching,
    "fast_matching":     run_fast_matching,
    "stable_matching":   run_stable_matching,
    "run_all":           run_all_methods,
    "weighted_matching": run_weighted_matching,
    "balanced_matching": run_balanced_matching,
    "custom":            run_stable_matching,  # safe fallback
}


# =============================================================================
# SECTION 10: MAIN APPLICATION WINDOW
# =============================================================================

class MainWindow(QMainWindow):
    """
    Full application window integrating the SmartSelectionPanel.

    Layout:
      ┌─────────── header ────────────┐
      │ left panel    │ right panel   │
      │ (upload +     │ (results)     │
      │  smart panel) │               │
      └───────────────┴───────────────┘
      status bar
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TA–Course Matching System")
        self.setMinimumSize(980, 720)
        self._df: Optional[pd.DataFrame] = None
        self._build_ui()
        self._apply_global_style()

    # ── Build ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        # Header banner
        root.addWidget(self._build_header())

        # Split view
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([580, 380])
        root.addWidget(splitter, stretch=1)

        # Status bar
        self._status = QStatusBar()
        self._status.showMessage("Welcome!  Upload an Excel file to begin.")
        self.setStatusBar(self._status)

    def _build_header(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #3498db
                );
                border-radius: 10px;
            }
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 12, 20, 12)

        title = QLabel("🎓  TA–Course Matching System")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(title)
        layout.addStretch()

        sub = QLabel("Intelligent Assignment Tool")
        sub.setFont(QFont("Segoe UI", 10))
        sub.setStyleSheet("color: #bdc3c7; background: transparent;")
        layout.addWidget(sub)
        return frame

    def _build_left_panel(self) -> QWidget:
        """File upload section + Smart Selection Panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(12)

        # ── Upload section ────────────────────────────────────────────────
        upload = QFrame()
        upload.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px dashed #bdc3c7;
                border-radius: 10px;
            }
        """)
        ul = QVBoxLayout(upload)
        ul.setContentsMargins(16, 12, 16, 12)
        ul.setSpacing(8)

        step1 = QLabel("📂  Step 1: Upload Your Data File")
        step1.setFont(QFont("Segoe UI", 12, QFont.Bold))
        step1.setStyleSheet("color: #2c3e50;")
        ul.addWidget(step1)

        hint = QLabel(
            "Upload an Excel (.xlsx) or CSV file containing TA preferences, "
            "course list, and capacities."
        )
        hint.setFont(QFont("Segoe UI", 10))
        hint.setStyleSheet("color: #7f8c8d;")
        hint.setWordWrap(True)
        ul.addWidget(hint)

        file_row = QHBoxLayout()

        self._file_label = QLabel("No file selected")
        self._file_label.setFont(QFont("Segoe UI", 10))
        self._file_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                background: #f8f9fa;
                border: 1px solid #dfe6e9;
                border-radius: 6px;
                padding: 6px 10px;
            }
        """)
        file_row.addWidget(self._file_label, stretch=1)

        browse_btn = QPushButton("Browse File")
        browse_btn.setStyleSheet("""
            QPushButton {
                background: #3498db; color: white;
                border: none; border-radius: 6px;
                padding: 6px 16px; font-size: 11px; font-weight: bold;
            }
            QPushButton:hover { background: #2980b9; }
        """)
        browse_btn.clicked.connect(self._browse_file)
        file_row.addWidget(browse_btn)

        self._clear_btn = QPushButton("✕")
        self._clear_btn.setFixedWidth(30)
        self._clear_btn.setEnabled(False)
        self._clear_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c; color: white;
                border: none; border-radius: 6px;
            }
            QPushButton:hover  { background: #c0392b; }
            QPushButton:disabled { background: #bdc3c7; }
        """)
        self._clear_btn.clicked.connect(self._clear_file)
        file_row.addWidget(self._clear_btn)

        ul.addLayout(file_row)
        layout.addWidget(upload)

        # ── Smart panel ───────────────────────────────────────────────────
        step2 = QLabel("⚙️  Step 2: Choose Matching Strategy")
        step2.setFont(QFont("Segoe UI", 12, QFont.Bold))
        step2.setStyleSheet("color: #2c3e50;")
        layout.addWidget(step2)

        self._smart_panel = SmartSelectionPanel()
        self._smart_panel.strategy_selected.connect(self._on_strategy_selected)
        layout.addWidget(self._smart_panel, stretch=1)

        return widget

    def _build_right_panel(self) -> QWidget:
        """Results display panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(8)

        results_title = QLabel("📋  Results")
        results_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        results_title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(results_title)

        self._results_display = QTextEdit()
        self._results_display.setReadOnly(True)
        self._results_display.setFont(QFont("Consolas", 10))
        self._results_display.setStyleSheet("""
            QTextEdit {
                background: #2c3e50;
                color: #2ecc71;
                border-radius: 8px;
                padding: 12px;
                border: none;
            }
        """)
        self._results_display.setPlaceholderText(
            "Results will appear here after running the matching...\n\n"
            "Steps:\n"
            "  1. Upload your Excel file\n"
            "  2. Review the smart recommendation\n"
            "  3. Click  ▶ Run Matching"
        )
        layout.addWidget(self._results_display, stretch=1)

        self._export_btn = QPushButton("💾  Export Results to Excel")
        self._export_btn.setEnabled(False)
        self._export_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60; color: white;
                border: none; border-radius: 6px;
                padding: 8px 16px; font-size: 11px;
            }
            QPushButton:hover    { background: #229954; }
            QPushButton:disabled { background: #95a5a6; }
        """)
        layout.addWidget(self._export_btn)
        return widget

    # ── Event handlers ────────────────────────────────────────────────────

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Data File", "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return

        try:
            self._df = (
                pd.read_csv(path) if path.endswith(".csv")
                else pd.read_excel(path)
            )

            filename = path.replace("\\", "/").split("/")[-1]
            self._file_label.setText(f"✅  {filename}  ({len(self._df)} rows)")
            self._file_label.setStyleSheet("""
                QLabel {
                    color: #27ae60;
                    background: #eafaf1;
                    border: 1px solid #2ecc71;
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-weight: bold;
                }
            """)
            self._clear_btn.setEnabled(True)
            self._status.showMessage(
                f"File loaded: {filename} — {len(self._df)} rows, "
                f"{len(self._df.columns)} columns. Analysing…"
            )
            self._smart_panel.load_dataframe(self._df)

        except Exception as exc:
            QMessageBox.critical(
                self, "File Error",
                f"Could not read the file:\n{exc}\n\n"
                "Please check the file format and try again."
            )

    def _clear_file(self):
        self._df = None
        self._file_label.setText("No file selected")
        self._file_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                background: #f8f9fa;
                border: 1px solid #dfe6e9;
                border-radius: 6px;
                padding: 6px 10px;
            }
        """)
        self._clear_btn.setEnabled(False)
        self._smart_panel.reset()
        self._results_display.clear()
        self._export_btn.setEnabled(False)
        self._status.showMessage("File cleared. Upload a new file to begin.")

    @pyqtSlot(str)
    def _on_strategy_selected(self, backend_key: str):
        """Route the selected backend key to the appropriate algorithm."""
        if self._df is None:
            QMessageBox.warning(self, "No Data", "Please upload a file first.")
            return

        self._status.showMessage(f"Running matching…  (method: {backend_key})")
        self._results_display.clear()

        try:
            func   = BACKEND_FUNCTIONS.get(backend_key, run_auto_matching)
            result = func(self._df)
            self._display_results(result, backend_key)
            self._export_btn.setEnabled(True)
            self._status.showMessage("✅ Matching complete!")
        except Exception as exc:
            self._results_display.setPlainText(
                f"❌ Error during matching:\n{exc}"
            )
            self._status.showMessage("❌ Matching failed — see results panel.")

    def _display_results(self, result: dict, backend_key: str):
        lines = [
            "=" * 52,
            "   MATCHING RESULTS",
            "=" * 52,
            f"   Method used    :  {result.get('method', backend_key)}",
            f"   Matched pairs  :  {result.get('matched_pairs', 'N/A')}",
            f"   Status         :  {result.get('status', 'unknown')}",
            "",
        ]

        if "results" in result:
            lines.append("   Comparison across methods:")
            lines.append("-" * 40)
            for method, res in result["results"].items():
                lines.append(
                    f"   [{method:<16}]  pairs = {res.get('matched_pairs','?')}"
                )

        lines += [
            "",
            "=" * 52,
            "   ✅ Matching completed successfully!",
            "      Click 'Export Results' to save.",
            "=" * 52,
        ]
        self._results_display.setPlainText("\n".join(lines))

    def _apply_global_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f2f5; }
            QWidget      { font-family: 'Segoe UI', Arial, sans-serif; }
            QSplitter::handle { background-color: #dfe6e9; width: 2px; }
            QToolTip {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 6px;
                font-size: 11px;
            }
        """)


# =============================================================================
# SECTION 11: ENTRY POINT
# =============================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    # ── Demo: auto-load sample data so you can test without a real file ───
    sample_df = pd.DataFrame({
        "ta_id":     ["TA1","TA1","TA1","TA2","TA2","TA3","TA4","TA5","TA5"],
        "course_id": ["C1", "C2", "C3", "C1", "C3", "C2", "C3", "C1", "C2"],
        "capacity":  [1,    1,    2,    1,    2,    1,    2,    1,    1  ],
        "utility":   [0.9,  0.7,  0.6,  0.8,  0.65, 0.95, 0.85, 0.75, 0.80],
    })

    # Simulate file loaded
    window._df = sample_df
    window._file_label.setText("✅  sample_data.xlsx  (9 rows)")
    window._file_label.setStyleSheet("""
        QLabel {
            color: #27ae60;
            background: #eafaf1;
            border: 1px solid #2ecc71;
            border-radius: 6px;
            padding: 6px 10px;
            font-weight: bold;
        }
    """)
    window._clear_btn.setEnabled(True)
    window._smart_panel.load_dataframe(sample_df)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()