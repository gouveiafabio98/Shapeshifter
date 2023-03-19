import os
import json

def loadJSON(path):
    addon_dir = os.path.dirname(__file__)
    file_path = os.path.join(addon_dir, path)

    with open(file_path, "r") as f:
        data = json.load(f)
    return data