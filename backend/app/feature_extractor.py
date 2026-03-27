from collections import Counter
from datetime import datetime
import numpy as np
import math


def extract_features(logs: list[dict]) -> dict:
    error_count = 0
    warn_count = 0
    info_count = 0
    critical_count = 0
    failed_login_count = 0

    timestamps = []
    unique_ips = set()
    messages = []

    for log in logs:
        level = log.get("level", "").upper()
        message = log.get("message", "").lower()
        messages.append(message)

        if level == "ERROR":
            error_count += 1
        elif level in ("WARN", "WARNING"):
            warn_count += 1
        elif level == "INFO":
            info_count += 1
        elif level == "CRITICAL":
            critical_count += 1

        if "failed login" in message:
            failed_login_count += 1

        # Timestamp handling
        try:
            timestamps.append(datetime.fromisoformat(log["timestamp"].replace("Z", "")))
        except:
            pass

        # IP detection
        for token in message.split():
            if token.count(".") == 3:
                unique_ips.add(token)

    total_logs = len(logs)

    # ? Time gap feature
    timestamps.sort()
    time_diffs = np.diff(timestamps) if len(timestamps) > 1 else []
    avg_time_gap = np.mean([td.total_seconds() for td in time_diffs]) if len(time_diffs) else 0

    # ?? Entropy feature
    counter = Counter(messages)
    probs = [v / total_logs for v in counter.values()]
    entropy = -sum(p * math.log2(p) for p in probs) if probs else 0

    return {
        "error_count": error_count,
        "warn_count": warn_count,
        "info_count": info_count,
        "critical_count": critical_count,
        "failed_login_count": failed_login_count,
        "total_logs": total_logs,
        "unique_ip_count": len(unique_ips),

        # NEW FEATURES
        "avg_time_gap": round(avg_time_gap, 4),
        "log_entropy": round(entropy, 4),
    }
    