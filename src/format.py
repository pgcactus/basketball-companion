import sys

from schema import SessionAnalysis

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


def _supports_color() -> bool:
    return sys.stdout.isatty()


def format_session(analysis: SessionAnalysis) -> str:
    use_color = _supports_color()

    made = sum(1 for s in analysis.shots if s.result == "made")
    missed = sum(1 for s in analysis.shots if s.result == "missed")
    total = len(analysis.shots)

    lines = [f"Made: {made}  Missed: {missed}  ({total} shots)", ""]

    for shot in analysis.shots:
        if shot.result == "made":
            marker = f"{GREEN}✓ MADE{RESET}" if use_color else "✓ MADE"
        else:
            marker = f"{RED}✗ MISSED{RESET}" if use_color else "✗ MISSED"
        lines.append(
            f"{shot.timestamp_of_outcome}  {marker}  {shot.shot_type}  —  {shot.feedback}"
        )

    lines.append("")
    lines.append(f"Summary: {analysis.session_summary}")

    return "\n".join(lines)
