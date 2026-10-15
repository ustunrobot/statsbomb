"""
Single-active-user authentication layer.

Two separate concerns, kept deliberately independent:

1. Login (`is_authenticated` / the Flask `session` cookie): "has this browser
   proved it knows the password". Long-lived (PERMANENT_SESSION_LIFETIME),
   so a returning user isn't asked to log in again every visit.

2. The active slot (`try_claim` / `touch` / `release`): "which single logged-in
   session is currently allowed to use the app". Short-lived - released
   automatically if its holder goes quiet for STALE_SECONDS (tab closed,
   laptop shut) - so a second user isn't locked out indefinitely by someone
   who simply walked away without logging out.

The active slot is a single in-process dict guarded by a lock. This only
works correctly with a single worker process (see the `-w 1` gunicorn flag
in the deployment notes) - multiple processes would each keep their own
copy and the lock would do nothing.

One user is protected from being force-kicked: PROTECTED_USER ("admin") can
force-claim the slot from anyone, but nobody else can force-claim it away
from admin - every other pair of users can force-claim from each other
freely. This is enforced here in try_claim(), not just hidden in the
frontend, so a direct API call can't bypass it either.

Every login attempt (success or failure) is appended to logs/auth.jsonl via
log_login_attempt() - one JSON object per line, so a record survives a
crash mid-write and the file never needs a full read-modify-write to append
(unlike a single JSON array, which would require re-parsing and rewriting
the whole file on every login).
"""

import json
import time
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

STALE_SECONDS = 90
PROTECTED_USER = "admin"

LOG_FILE = Path(__file__).parent / "logs" / "auth.jsonl"

_lock = threading.Lock()
_active = {"sid": None, "user": None, "last_seen": 0.0}

_log_lock = threading.Lock()


def new_sid() -> str:
    return uuid.uuid4().hex


def _is_stale(last_seen: float) -> bool:
    return (time.time() - last_seen) > STALE_SECONDS


def slot_holder():
    """Return {'user', 'last_seen'} for the current holder, or None if the slot is free/stale."""
    with _lock:
        if _active["sid"] is None or _is_stale(_active["last_seen"]):
            return None
        return {"user": _active["user"], "last_seen": _active["last_seen"]}


def try_claim(sid: str, user: str, force: bool = False):
    """
    Attempt to make `sid` the active slot holder.

    Returns (True, None) on success - either the slot was free/stale, already
    held by this sid, or `force` was set and allowed.
    Returns (False, {'user', 'last_seen', 'can_force'}) if someone else holds
    it and the claim didn't go through - either `force` wasn't set, or the
    holder is PROTECTED_USER and `user` isn't (see module docstring).
    """
    with _lock:
        holder_sid = _active["sid"]
        holder_user = _active["user"]
        free_or_stale = holder_sid is None or _is_stale(_active["last_seen"])

        if free_or_stale or holder_sid == sid:
            _active["sid"] = sid
            _active["user"] = user
            _active["last_seen"] = time.time()
            return True, None

        can_force = not (holder_user == PROTECTED_USER and user != PROTECTED_USER)

        if force and can_force:
            _active["sid"] = sid
            _active["user"] = user
            _active["last_seen"] = time.time()
            return True, None

        return False, {"user": holder_user, "last_seen": _active["last_seen"], "can_force": can_force}


def touch(sid: str) -> bool:
    """Refresh last_seen for sid if it currently holds the slot. Returns whether it does."""
    with _lock:
        if _active["sid"] == sid:
            _active["last_seen"] = time.time()
            return True
        return False


def release(sid: str) -> None:
    """Give up the slot if `sid` currently holds it."""
    with _lock:
        if _active["sid"] == sid:
            _active["sid"] = None
            _active["user"] = None
            _active["last_seen"] = 0.0


def log_login_attempt(username: str, success: bool, reason: str, ip: str) -> None:
    """Append one JSON line to logs/auth.jsonl for every login attempt, successful or not."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "login_success" if success else "login_failure",
        "username": username,
        "reason": reason,
        "ip": ip,
    }
    try:
        with _log_lock:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
    except IOError as e:
        print(f"[auth] Failed to write login log entry: {e}")
