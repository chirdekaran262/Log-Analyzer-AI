import re


# Supports formats:
#   2024-01-01 12:00:00 ERROR Some message here
#   [2024-01-01 12:00:00] [ERROR] Some message
#   2024-01-01T12:00:00Z ERROR Some message
_LOG_PATTERN = re.compile(
    r"^[\[\(]?(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[\w:.+-]*)[\]\)]?"
    r"\s+[\[\(]?(?P<level>ERROR|WARN(?:ING)?|INFO|DEBUG|CRITICAL|NOTICE|FATAL)[\]\)]?"
    r"\s+(?P<message>.+)$",
    re.IGNORECASE,
)


def parse_log(file_path: str) -> list[dict]:
    """
    Parse a plain-text log file and return a list of structured log dicts.
    Lines that do not match the expected format are skipped.
    """
    logs = []

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
            for lineno, raw_line in enumerate(fh, start=1):
                line = raw_line.strip()
                if not line:
                    continue

                match = _LOG_PATTERN.match(line)
                if match:
                    logs.append(
                        {
                            "timestamp": match.group("timestamp"),
                            "level": match.group("level").upper(),
                            "message": match.group("message").strip(),
                            "raw": line,
                        }
                    )
                else:
                    # Fallback: split on whitespace, keep as INFO
                    parts = line.split(None, 3)
                    if len(parts) >= 3:
                        logs.append(
                            {
                                "timestamp": parts[0] + " " + parts[1] if len(parts) > 1 else parts[0],
                                "level": "INFO",
                                "message": " ".join(parts[2:]),
                                "raw": line,
                            }
                        )
    except (OSError, IOError) as exc:
        # Propagate as a clear error so FastAPI can return a 400
        raise ValueError(f"Could not read log file: {exc}") from exc

    return logs