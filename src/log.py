from datetime import datetime
import os
import json
import re

LOG_DIR = "data/logs"
LOG_PREFIX = "log"
MAX_SIZE_MB = 1

os.makedirs(LOG_DIR, exist_ok=True)


def get_latest_log_file():
    files = [f for f in os.listdir(LOG_DIR) if re.match(rf"{LOG_PREFIX}-\d+\.json", f)]
    if not files:
        return os.path.join(LOG_DIR, f"{LOG_PREFIX}-0.json")
    indices = [int(re.findall(rf"{LOG_PREFIX}-(\d+)\.json", f)[0]) for f in files]
    latest_index = max(indices)
    return os.path.join(LOG_DIR, f"{LOG_PREFIX}-{latest_index}.json")


def rotate_log_file_if_needed(current_file):
    if os.path.exists(current_file):
        size_mb = os.path.getsize(current_file) / (1024 * 1024)
        if size_mb >= MAX_SIZE_MB:
            current_index = int(
                re.findall(rf"{LOG_PREFIX}-(\d+)\.json", current_file)[0]
            )
            return os.path.join(LOG_DIR, f"{LOG_PREFIX}-{current_index + 1}.json")
    return current_file


def save_log(entry):
    current_file = get_latest_log_file()
    target_file = rotate_log_file_if_needed(current_file)

    if os.path.exists(target_file):
        with open(target_file, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)

    with open(target_file, "w") as f:
        json.dump(data, f, indent=2)


def add_log(text):
    entry = {"timestamp": datetime.now().isoformat(), "text": text}
    save_log(entry)
    print("Log added.")


def add_log_continuous():
    print("Enter your log (type 'EOF' on a new line to finish):")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "EOF":
            break
        lines.append(line)
    text = "\n".join(lines)
    add_log(text)
