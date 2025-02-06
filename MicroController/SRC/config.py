# config.py
import ujson

def load_config(filename="config.json"):
    try:
        with open(filename, "r") as f:
            return ujson.load(f)
    except Exception as e:
        print("Error loading config:", e)
        return {}
