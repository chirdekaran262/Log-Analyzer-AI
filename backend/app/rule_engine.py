"""
rule_engine.py
Deterministic rule-based incident detection over extracted feature dicts.
"""

# Thresholds – tune these for your environment
_ERROR_THRESHOLD = 10          # absolute error count
_ERROR_RATIO_THRESHOLD = 0.20  # 20 % of all logs are errors
_FAILED_LOGIN_THRESHOLD = 5
_CRITICAL_THRESHOLD = 1        # any critical triggers an alert
_WARN_RATIO_THRESHOLD = 0.40


def rule_based_detection(features: dict) -> list[str]:
    """Return a list of human-readable alert strings (empty = no alerts)."""
    incidents: list[str] = []

    if features.get("critical_count", 0) >= _CRITICAL_THRESHOLD:
        incidents.append(
            f"CRITICAL events detected ({features['critical_count']} occurrences)"
        )

    if features.get("error_count", 0) >= _ERROR_THRESHOLD:
        incidents.append(
            f"High absolute error count: {features['error_count']} errors"
        )

    if features.get("error_ratio", 0) >= _ERROR_RATIO_THRESHOLD:
        pct = round(features["error_ratio"] * 100, 1)
        incidents.append(
            f"Elevated error rate: {pct}% of all log entries are errors"
        )

    if features.get("failed_login_count", 0) >= _FAILED_LOGIN_THRESHOLD:
        incidents.append(
            f"Brute-force risk: {features['failed_login_count']} failed login attempts"
        )

    if features.get("warn_ratio", 0) >= _WARN_RATIO_THRESHOLD:
        pct = round(features["warn_ratio"] * 100, 1)
        incidents.append(
            f"Warning storm: {pct}% of entries are warnings"
        )

    if features.get("unique_ip_count", 0) > 20:
        incidents.append(
            f"Unusual source diversity: {features['unique_ip_count']} unique IPs in log"
        )

    return incidents