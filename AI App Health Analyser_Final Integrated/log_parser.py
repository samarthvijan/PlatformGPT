import re
import json

def infer_error_type(message):
    msg = message.lower()
    known_pattern = re.search(r"([a-zA-Z]+Error)", message)
    if known_pattern:
        return known_pattern.group(1)
    if "timeout" in msg:
        return "Timeout"
    if "not found" in msg:
        return "NotFound"
    if "failed" in msg:
        return "Failure"
    if "invalid" in msg:
        return "InvalidInput"
    if "permission" in msg or "unauthorized" in msg:
        return "PermissionDenied"
    if "unreachable" in msg:
        return "UnreachableService"
    if "503" in msg or "502" in msg:
        return "ServiceUnavailable"
    if "exception" in msg:
        return "Exception"
    return "Uncategorized"

def parse_logs(log_file="app_logs.txt", output_file="parsed_logs.txt"):
    log_pattern = re.compile(
        r"^(?P<timestamp>\S+)\s+\[(?P<level>ERROR|WARNING|INFO|DEBUG|SUCCESS)\]\s+"
        r"(?P<source>\S+)\s+-\s+(?P<message>.*)$"
    )
    parsed = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            match = log_pattern.match(line.strip())
            if not match:
                continue
            level = match.group("level")
            if level not in {"ERROR", "WARNING"}:
                continue
            timestamp = match.group("timestamp")
            source = match.group("source")
            message = match.group("message").strip()
            error_type = infer_error_type(message)
            parsed.append({
                "timestamp": timestamp,
                "level": level,
                "service": source,
                "message": message,
                "error_type": error_type,
                "context": source
            })
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(parsed, out, indent=2)

    return parsed