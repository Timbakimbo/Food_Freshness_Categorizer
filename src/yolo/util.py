import glob
import re
import os

def get_next_index(folder="data/yolo", prefix="output"):
    files = glob.glob(os.path.join(folder, f"{prefix}_*.jpg"))
    indices = []

    for f in files:
        match = re.search(rf"{prefix}_(\d+)\.jpg$", os.path.basename(f))
        if match:
            indices.append(int(match.group(1)))

    return max(indices, default=-1) + 1