# bob/session.py

import os
import json
import uuid
import datetime
from .config import SESSION_FILE, SESSION_DURATION_DAYS, DEVICE_ID

def generate_session_data() -> dict:
    """
    Create a new session id using the device id, current timestamp, and a random UUID.
    Returns a dictionary with the session ID and its creation time.
    """
    timestamp = datetime.datetime.now()
    session_uuid = uuid.uuid4().hex  # Random 32-character hex string.
    session_id = f"{DEVICE_ID}-{timestamp.strftime('%Y%m%d%H%M%S')}-{session_uuid}"
    return {
        "session_id": session_id,
        "created_at": timestamp.isoformat()
    }

def save_session(session_data: dict):
    """
    Save the session data to a file.
    """
    with open(SESSION_FILE, 'w') as f:
        json.dump(session_data, f)

def load_session() -> dict:
    """
    Load the session data from the file.
    """
    with open(SESSION_FILE, 'r') as f:
        return json.load(f)

def is_session_valid(session_data: dict) -> bool:
    """
    Check if the saved session is still within the allowed duration.
    """
    try:
        created_at = datetime.datetime.fromisoformat(session_data["created_at"])
        now = datetime.datetime.now()
        # Valid if the session is less than SESSION_DURATION_DAYS old.
        return (now - created_at).days < SESSION_DURATION_DAYS
    except Exception:
        return False

def get_session() -> str:
    """
    Retrieve a session ID from the file. If it does not exist or is expired,
    generate a new session ID, save it, and return it.
    """
    if os.path.exists(SESSION_FILE):
        try:
            session_data = load_session()
            if is_session_valid(session_data):
                return session_data["session_id"]
        except Exception:
            # In case of an error reading or parsing, fall through to generate a new session.
            pass

    # No valid session exists; generate and save a new one.
    session_data = generate_session_data()
    save_session(session_data)
    return session_data["session_id"]

def clear_session():
    """
    Optionally, clear the session so that a new one will be created (e.g., at deployment end).
    """
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
