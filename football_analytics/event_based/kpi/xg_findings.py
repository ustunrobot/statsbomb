"""
XG Findings Layer: Evaluates xG metrics against a comprehensive catalog of findings.

Implements findings from the xG Evaluated Findings Catalogue covering:
- Overall Attacking Performance
- Chance Creation & Quality
- Attacking Profiles
- Set Pieces
- Finishing & Aerial Attack
- Defending (Process, Shot Suppression, Chance Quality)
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Finding:
    """Represents a triggered finding."""
    category: str
    finding_name: str
    description: str
    team_id: int
    team_name: str


def get_finding_evidence(finding_name: str, team_metrics: Dict) -> str:
    """Return relevant metric evidence for a finding."""
    def get_value(metric_obj):
        return metric_obj.value if hasattr(metric_obj, 'value') else 0.0
    def get_pct(metric_obj):
        return metric_obj.percentile if hasattr(metric_obj, 'percentile') else 0.0

    evidence_map = {
        "Elite attacking output": lambda: f"xGF: {get_value(team_metrics.get('xgf')):.2f} ({get_pct(team_metrics.get('xgf')):.0f}th %ile)",
        "Strong attacking output": lambda: f"xGF: {get_value(team_metrics.get('xgf')):.2f} ({get_pct(team_metrics.get('xgf')):.0f}th %ile)",
        "Very weak attacking output": lambda: f"xGF: {get_value(team_metrics.get('xgf')):.2f} ({get_pct(team_metrics.get('xgf')):.0f}th %ile)",
        "Weak attacking output": lambda: f"xGF: {get_value(team_metrics.get('xgf')):.2f} ({get_pct(team_metrics.get('xgf')):.0f}th %ile)",
        "Low Goal output": lambda: f"Goals: {get_value(team_metrics.get('goals')):.0f} ({get_pct(team_metrics.get('goals')):.0f}th %ile)",
        "High Goal output": lambda: f"Goals: {get_value(team_metrics.get('goals')):.0f} ({get_pct(team_metrics.get('goals')):.0f}th %ile)",
        "High shooting volume": lambda: f"Shots: {get_value(team_metrics.get('shots')):.0f} ({get_pct(team_metrics.get('shots')):.0f}th %ile)",
        "Low shooting volume": lambda: f"Shots: {get_value(team_metrics.get('shots')):.0f} ({get_pct(team_metrics.get('shots')):.0f}th %ile)",
        "High shot quality": lambda: f"xG/Shot: {get_value(team_metrics.get('xgf')) / max(1, get_value(team_metrics.get('shots'))):.3f}",
        "Low shot quality": lambda: f"xG/Shot: {get_value(team_metrics.get('xgf')) / max(1, get_value(team_metrics.get('shots'))):.3f}",
        "Clinical finishing": lambda: f"Goals: {get_value(team_metrics.get('goals')):.0f}, xGF: {get_value(team_metrics.get('xgf')):.2f}, Diff: +{get_value(team_metrics.get('goals')) - get_value(team_metrics.get('xgf')):.2f}",
        "Finishing underperformance": lambda: f"Goals: {get_value(team_metrics.get('goals')):.0f}, xGF: {get_value(team_metrics.get('xgf')):.2f}, Diff: {get_value(team_metrics.get('goals')) - get_value(team_metrics.get('xgf')):.2f}",
        "High conversion of shooting opportunities": lambda: f"Conversion: {get_value(team_metrics.get('goals')) / max(1, get_value(team_metrics.get('shots'))) * 100:.1f}%",
        "Low conversion": lambda: f"Conversion: {get_value(team_metrics.get('goals')) / max(1, get_value(team_metrics.get('shots'))) * 100:.1f}%",
        "Strong aerial scoring threat": lambda: f"xG Headers: {get_value(team_metrics.get('xgf_headers')):.2f}",
        "Low aerial threat": lambda: f"xG Headers: {get_value(team_metrics.get('xgf_headers')):.2f}",
        "Elite defensive process": lambda: f"xGA: {get_value(team_metrics.get('xga')):.2f} ({get_pct(team_metrics.get('xga')):.0f}th %ile)",
        "Strong defensive process": lambda: f"xGA: {get_value(team_metrics.get('xga')):.2f} ({get_pct(team_metrics.get('xga')):.0f}th %ile)",
        "Weak defensive process": lambda: f"xGA: {get_value(team_metrics.get('xga')):.2f} ({get_pct(team_metrics.get('xga')):.0f}th %ile)",
        "Very weak defensive process": lambda: f"xGA: {get_value(team_metrics.get('xga')):.2f} ({get_pct(team_metrics.get('xga')):.0f}th %ile)",
        "Strong shot suppression": lambda: f"Opponent Shots: {get_value(team_metrics.get('op_shots')):.0f} ({get_pct(team_metrics.get('op_shots')):.0f}th %ile)",
        "Poor shot suppression": lambda: f"Opponent Shots: {get_value(team_metrics.get('op_shots')):.0f} ({get_pct(team_metrics.get('op_shots')):.0f}th %ile)",
        "Defensive overperformance": lambda: f"Goals Conceded: {get_value(team_metrics.get('goals_conceded')):.0f}, xGA: {get_value(team_metrics.get('xga')):.2f}, Diff: {get_value(team_metrics.get('goals_conceded')) - get_value(team_metrics.get('xga')):.2f}",
        "Defensive underperformance": lambda: f"Goals Conceded: {get_value(team_metrics.get('goals_conceded')):.0f}, xGA: {get_value(team_metrics.get('xga')):.2f}, Diff: {get_value(team_metrics.get('goals_conceded')) - get_value(team_metrics.get('xga')):.2f}",
        "Attack outperforming process": lambda: f"Goals: {get_value(team_metrics.get('goals')):.0f}, xGF: {get_value(team_metrics.get('xgf')):.2f}, +{get_value(team_metrics.get('goals')) - get_value(team_metrics.get('xgf')):.2f}",
        "Attack underperforming process": lambda: f"Goals: {get_value(team_metrics.get('goals')):.0f}, xGF: {get_value(team_metrics.get('xgf')):.2f}, {get_value(team_metrics.get('goals')) - get_value(team_metrics.get('xgf')):.2f}",
        "Defence outperforming process": lambda: f"Conceded: {get_value(team_metrics.get('goals_conceded')):.0f}, xGA: {get_value(team_metrics.get('xga')):.2f}, {get_value(team_metrics.get('goals_conceded')) - get_value(team_metrics.get('xga')):.2f}",
        "Defence underperforming process": lambda: f"Conceded: {get_value(team_metrics.get('goals_conceded')):.0f}, xGA: {get_value(team_metrics.get('xga')):.2f}, +{get_value(team_metrics.get('goals_conceded')) - get_value(team_metrics.get('xga')):.2f}",
        "Open-play dominant attack": lambda: f"Open Play xGF: {get_value(team_metrics.get('xgf_open_play')):.2f}",
        "Set-piece dependent attack": lambda: f"Set Piece xGF: {(get_value(team_metrics.get('xgf_penalty')) + get_value(team_metrics.get('xgf_corner')) + get_value(team_metrics.get('xgf_free_kick'))):.2f}",
        "Low set-piece reliance": lambda: f"Set Piece xGF share: {(get_value(team_metrics.get('xgf_penalty')) + get_value(team_metrics.get('xgf_corner')) + get_value(team_metrics.get('xgf_free_kick'))) / max(0.01, get_value(team_metrics.get('xgf'))) * 100:.0f}%",
        "Strong corner threat": lambda: f"Corner xGF: {get_value(team_metrics.get('xgf_corner')):.2f}",
        "Weak corner threat": lambda: f"Corner xGF: {get_value(team_metrics.get('xgf_corner')):.2f}",
        "Strong free-kick threat": lambda: f"Free Kick xGF: {get_value(team_metrics.get('xgf_free_kick')):.2f}",
        "Weak free-kick threat": lambda: f"Free Kick xGF: {get_value(team_metrics.get('xgf_free_kick')):.2f}",
    }

    if finding_name in evidence_map:
        try:
            return evidence_map[finding_name]()
        except:
            return None
    return None


class XGFindingsLayer:
    """Evaluates xG metrics against comprehensive findings catalog."""

    def __init__(self):
        self.layer_name = "xg_findings"

    def evaluate_team(self, team_id: int, team_name: str, team_metrics: Dict) -> List[Finding]:
        """
        Evaluate all findings for a team.

        Args:
            team_id: Team identifier
            team_name: Team name
            team_metrics: Team's aggregated metrics with Metric objects

        Returns:
            List of triggered findings for this team
        """
        findings = []

        def get_value(metric_obj):
            """Extract value from Metric object."""
            return metric_obj.value if hasattr(metric_obj, 'value') else 0.0

        def get_pct(metric_obj):
            """Extract percentile from Metric object."""
            return metric_obj.percentile if hasattr(metric_obj, 'percentile') else 0.0

        # Extract metric values
        xgf_val = get_value(team_metrics.get('xgf'))
        xgf_pct = get_pct(team_metrics.get('xgf'))
        xga_val = get_value(team_metrics.get('xga'))
        xga_pct = get_pct(team_metrics.get('xga'))
        goals_val = get_value(team_metrics.get('goals'))
        goals_pct = get_pct(team_metrics.get('goals'))
        goals_conceded_val = get_value(team_metrics.get('goals_conceded'))
        shots_val = get_value(team_metrics.get('shots'))
        shots_pct = get_pct(team_metrics.get('shots'))

        xgf_open_play_val = get_value(team_metrics.get('xgf_open_play'))
        xgf_penalty_val = get_value(team_metrics.get('xgf_penalty'))
        xgf_corner_val = get_value(team_metrics.get('xgf_corner'))
        xgf_free_kick_val = get_value(team_metrics.get('xgf_free_kick'))
        xgf_headers_val = get_value(team_metrics.get('xgf_headers'))

        goals_open_play_val = get_value(team_metrics.get('goals_open_play'))
        goals_corner_val = get_value(team_metrics.get('goals_corner'))
        goals_free_kick_val = get_value(team_metrics.get('goals_free_kick'))
        goals_headers_val = get_value(team_metrics.get('goals_headers'))

        op_shots_pct = get_pct(team_metrics.get('op_shots'))

        # ===== OVERALL ATTACKING PERFORMANCE =====
        if xgf_pct >= 90:
            findings.append(Finding(
                category="Overall Attacking Performance",
                finding_name="Elite attacking output",
                description="Exceptional expected-goal production.",
                team_id=team_id,
                team_name=team_name
            ))
        elif xgf_pct >= 80:
            findings.append(Finding(
                category="Overall Attacking Performance",
                finding_name="Strong attacking output",
                description="Team generates substantially more xG than the benchmark.",
                team_id=team_id,
                team_name=team_name
            ))

        if xgf_pct <= 10:
            findings.append(Finding(
                category="Overall Attacking Performance",
                finding_name="Very weak attacking output",
                description="Exceptionally low xG production.",
                team_id=team_id,
                team_name=team_name
            ))
        elif xgf_pct <= 20:
            findings.append(Finding(
                category="Overall Attacking Performance",
                finding_name="Weak attacking output",
                description="Team generates substantially less xG than the benchmark.",
                team_id=team_id,
                team_name=team_name
            ))
        if goals_pct <= 20:
            findings.append(Finding(
                category="Overall Attacking Performance",
                finding_name="Low Goal output",
                description="Team scores at a high rate.",
                team_id=team_id,
                team_name=team_name
            ))
        elif goals_pct >= 80:
            findings.append(Finding(
                category="Overall Attacking Performance",
                finding_name="High Goal output",
                description="Team scores at a high rate.",
                team_id=team_id,
                team_name=team_name
            ))

        # ===== CHANCE CREATION =====
        if shots_pct >= 80:
            findings.append(Finding(
                category="Chance Creation",
                finding_name="High shooting volume",
                description="Team produces a large number of shots.",
                team_id=team_id,
                team_name=team_name
            ))
        if shots_pct <= 20:
            findings.append(Finding(
                category="Chance Creation",
                finding_name="Low shooting volume",
                description="Team produces relatively few shots.",
                team_id=team_id,
                team_name=team_name
            ))

        # ===== CHANCE QUALITY =====
        if shots_val > 0:
            xg_per_shot = xgf_val / shots_val
            if xg_per_shot >= 0.12:
                findings.append(Finding(
                    category="Chance Quality",
                    finding_name="High shot quality",
                    description="Team's average shot carries high expected-goal value.",
                    team_id=team_id,
                    team_name=team_name
                ))
            if xg_per_shot <= 0.08:
                findings.append(Finding(
                    category="Chance Quality",
                    finding_name="Low shot quality",
                    description="Team takes many relatively low-value shots.",
                    team_id=team_id,
                    team_name=team_name
                ))

        # ===== ATTACKING PROFILE =====
        if xgf_val > 0:
            set_piece_xg = xgf_penalty_val + xgf_corner_val + xgf_free_kick_val
            set_piece_share = set_piece_xg / xgf_val

            if xgf_open_play_val / xgf_val >= 0.80:
                findings.append(Finding(
                    category="Attacking Profile",
                    finding_name="Open-play dominant attack",
                    description="Most attacking xG comes from open play.",
                    team_id=team_id,
                    team_name=team_name
                ))
            if set_piece_share >= 0.20:
                findings.append(Finding(
                    category="Attacking Profile",
                    finding_name="Set-piece dependent attack",
                    description="Unusually large share of xG comes from set pieces.",
                    team_id=team_id,
                    team_name=team_name
                ))
            if set_piece_share <= 0.10:
                findings.append(Finding(
                    category="Attacking Profile",
                    finding_name="Low set-piece reliance",
                    description="Attacking output is overwhelmingly open-play based.",
                    team_id=team_id,
                    team_name=team_name
                ))

        # ===== SET PIECES =====
        if xgf_corner_val >= 0.5:
            findings.append(Finding(
                category="Set Pieces",
                finding_name="Strong corner threat",
                description="Corners consistently generate significant xG.",
                team_id=team_id,
                team_name=team_name
            ))
        if xgf_corner_val <= 0.1:
            findings.append(Finding(
                category="Set Pieces",
                finding_name="Weak corner threat",
                description="Corners produce little xG.",
                team_id=team_id,
                team_name=team_name
            ))

        if xgf_free_kick_val >= 0.5:
            findings.append(Finding(
                category="Set Pieces",
                finding_name="Strong free-kick threat",
                description="Free kicks produce substantial xG.",
                team_id=team_id,
                team_name=team_name
            ))
        if xgf_free_kick_val <= 0.1:
            findings.append(Finding(
                category="Set Pieces",
                finding_name="Weak free-kick threat",
                description="Free kicks produce little xG.",
                team_id=team_id,
                team_name=team_name
            ))

        # ===== FINISHING =====
        goal_diff = goals_val - xgf_val
        if goal_diff >= 1.0:
            findings.append(Finding(
                category="Finishing",
                finding_name="Clinical finishing",
                description="Team scores substantially more than expected from its chances.",
                team_id=team_id,
                team_name=team_name
            ))
        if goal_diff <= -1.0:
            findings.append(Finding(
                category="Finishing",
                finding_name="Finishing underperformance",
                description="Team scores substantially fewer than expected.",
                team_id=team_id,
                team_name=team_name
            ))

        if shots_val > 0:
            conversion_rate = goals_val / shots_val
            if conversion_rate >= 0.15:
                findings.append(Finding(
                    category="Finishing",
                    finding_name="High conversion of shooting opportunities",
                    description="High proportion of shots become goals.",
                    team_id=team_id,
                    team_name=team_name
                ))
            if conversion_rate <= 0.05:
                findings.append(Finding(
                    category="Finishing",
                    finding_name="Low conversion",
                    description="Low proportion of shots become goals.",
                    team_id=team_id,
                    team_name=team_name
                ))

        # ===== AERIAL ATTACK =====
        if xgf_headers_val >= 0.5:
            findings.append(Finding(
                category="Aerial Attack",
                finding_name="Strong aerial scoring threat",
                description="Headers contribute substantial attacking xG.",
                team_id=team_id,
                team_name=team_name
            ))
        if xgf_headers_val <= 0.1:
            findings.append(Finding(
                category="Aerial Attack",
                finding_name="Low aerial threat",
                description="Headers contribute little attacking xG.",
                team_id=team_id,
                team_name=team_name
            ))

        # ===== DEFENDING =====
        if xga_pct <= 10:
            findings.append(Finding(
                category="Defending",
                finding_name="Elite defensive process",
                description="Exceptionally low xGA.",
                team_id=team_id,
                team_name=team_name
            ))
        elif xga_pct <= 20:
            findings.append(Finding(
                category="Defending",
                finding_name="Strong defensive process",
                description="Team restricts opponents to low xG.",
                team_id=team_id,
                team_name=team_name
            ))

        if xga_pct >= 90:
            findings.append(Finding(
                category="Defending",
                finding_name="Very weak defensive process",
                description="Exceptionally high xGA.",
                team_id=team_id,
                team_name=team_name
            ))
        elif xga_pct >= 80:
            findings.append(Finding(
                category="Defending",
                finding_name="Weak defensive process",
                description="Opponents generate substantial xG.",
                team_id=team_id,
                team_name=team_name
            ))

        # ===== DEFENSIVE SHOT SUPPRESSION =====
        if op_shots_pct <= 20:
            findings.append(Finding(
                category="Defensive Shot Suppression",
                finding_name="Strong shot suppression",
                description="Opponents take relatively few shots.",
                team_id=team_id,
                team_name=team_name
            ))
        if op_shots_pct >= 80:
            findings.append(Finding(
                category="Defensive Shot Suppression",
                finding_name="Poor shot suppression",
                description="Opponents generate high shot volume.",
                team_id=team_id,
                team_name=team_name
            ))

        # ===== DEFENSIVE EFFICIENCY =====
        conceded_diff = goals_conceded_val - xga_val
        if conceded_diff <= -1.0:
            findings.append(Finding(
                category="Defensive Efficiency",
                finding_name="Defensive overperformance",
                description="Fewer goals conceded than expected.",
                team_id=team_id,
                team_name=team_name
            ))
        if conceded_diff >= 1.0:
            findings.append(Finding(
                category="Defensive Efficiency",
                finding_name="Defensive underperformance",
                description="More goals conceded than expected.",
                team_id=team_id,
                team_name=team_name
            ))

        # ===== PROCESS VS OUTCOME =====
        if goal_diff >= 1.5:
            findings.append(Finding(
                category="Process vs Outcome",
                finding_name="Attack outperforming process",
                description="Scoring output is substantially above the underlying xG process.",
                team_id=team_id,
                team_name=team_name
            ))
        if goal_diff <= -1.5:
            findings.append(Finding(
                category="Process vs Outcome",
                finding_name="Attack underperforming process",
                description="Scoring output is substantially below the underlying xG process.",
                team_id=team_id,
                team_name=team_name
            ))

        if conceded_diff <= -1.5:
            findings.append(Finding(
                category="Process vs Outcome",
                finding_name="Defence outperforming process",
                description="Goals conceded are substantially below xGA.",
                team_id=team_id,
                team_name=team_name
            ))
        if conceded_diff >= 1.5:
            findings.append(Finding(
                category="Process vs Outcome",
                finding_name="Defence underperforming process",
                description="Goals conceded are substantially above xGA.",
                team_id=team_id,
                team_name=team_name
            ))

        return findings

    def process_event_row(self, event_row: Dict, accumulator, team_ids: Dict = None):
        """Not used for findings layer."""
        pass

    def aggregate(self, team_aggregates: Dict, team_id: int, match_data: Dict) -> None:
        """Not used for findings layer."""
        pass
