# config.py
import ujson

def load_config(filename="config.json"):
    try:
        with open(filename, "r") as f:
            cfg = ujson.load(f)
        return cfg
    except Exception as e:
        print("Error loading config:", e)
        return {}
