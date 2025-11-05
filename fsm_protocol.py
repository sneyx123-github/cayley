import logging
from datetime import datetime

# Setup logging
logger = logging.getLogger("FSM_PROTOCOL")
logger.setLevel(logging.INFO)

# Aktuelle Protokollversion
PROTOCOL_VERSION = "1.0.0"

# Pflichtfelder für jede Nachricht
REQUIRED_FIELDS = ["msg_id", "cmd", "params", "sender", "version", "timestamp"]

def validate_message(msg: dict) -> bool:
    """
    Validiert die Struktur und Semantik einer FSM-Nachricht.
    - Prüft Pflichtfelder
    - Prüft Protokollversion
    - Prüft Zeitformat
    """
    if not isinstance(msg, dict):
        logger.warning("Nachricht ist kein Dictionary.")
        return False

    missing = [field for field in REQUIRED_FIELDS if field not in msg]
    if missing:
        logger.warning(f"Fehlende Felder: {missing}")
        return False

    if msg["version"] != PROTOCOL_VERSION:
        logger.warning(f"Version mismatch: {msg['version']} ≠ {PROTOCOL_VERSION}")
        return False

    try:
        datetime.fromisoformat(msg["timestamp"])
    except Exception:
        logger.warning(f"Ungültiges Zeitformat: {msg['timestamp']}")
        return False

    return True

def get_protocol_version() -> str:
    """Gibt die aktuelle Protokollversion zurück."""
    return PROTOCOL_VERSION

def is_valid_command(cmd: str) -> bool:
    """Prüft, ob der Befehl bekannt ist."""
    return cmd in ["reset_fsm", "vers", "ping", "init", "status"]

