import numpy as np
from collections import Counter


def extract_features(logs: list[dict]) -> dict:
    """
    Extract structured numerical features from a list of parsed log dicts.
    Each dict must contain at minimum: 'level' and 'message'.
    """
    error_count = 0
    warn_count = 0
    info_count = 0
    failed_login_count = 0
    critical_count = 0
    unique_ips = set()
    sources = []

    for log in logs:
        level = log.get("level", "").upper().strip()
        message = log.get("message", "").lower()

        if level == "ERROR":
            error_count += 1
        elif level in ("WARN", "WARNING"):
            warn_count += 1
        elif level == "INFO":
            info_count += 1
        elif level == "CRITICAL":
            critical_count += 1

        if "failed login" in message or "authentication failure" in message:
            failed_login_count += 1

        # Naive IP extraction: look for tokens that look like IPs
        for token in log.get("message", "").split():
            parts = token.strip("[](),").split(".")
            if len(parts) == 4 and all(p.isdigit() for p in parts):
                unique_ips.add(token.strip("[](),"))

        source = log.get("source", log.get("host", "unknown"))
        sources.append(source)

    total_logs = len(logs)
    error_ratio = error_count / total_logs if total_logs > 0 else 0.0
    warn_ratio = warn_count / total_logs if total_logs > 0 else 0.0
    top_sources = Counter(sources).most_common(3)

    return {
        "error_count": error_count,
        "warn_count": warn_count,
        "info_count": info_count,
        "critical_count": critical_count,
        "failed_login_count": failed_login_count,
        "total_logs": total_logs,
        "error_ratio": round(error_ratio, 4),
        "warn_ratio": round(warn_ratio, 4),
        "unique_ip_count": len(unique_ips),
        "top_sources": top_sources,
    }