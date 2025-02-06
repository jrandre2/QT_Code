# session.py
import os, ujson, utime, machine, urandom

SESSION_FILE = "session.json"

def generate_session():
    unique = machine.unique_id()
    timestamp = utime.time()
    rand_val = urandom.getrandbits(32)
    session_id = "{}-{}-{}".format(unique.hex(), timestamp, rand_val)
    return {"session_id": session_id, "created_at": timestamp}

def save_session(session_data):
    with open(SESSION_FILE, "w") as f:
        ujson.dump(session_data, f)

def load_session():
    try:
        with open(SESSION_FILE, "r") as f:
            return ujson.load(f)
    except Exception:
        return None

def get_session():
    session_data = load_session()
    if session_data is None:
        session_data = generate_session()
        save_session(session_data)
    return session_data.get("session_id")
