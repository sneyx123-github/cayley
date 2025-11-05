import logging
import redis
from cayley.fsm_protocol import validate_message
from cayley.fsm_state import fsm

# Setup logging
logger = logging.getLogger("FSM_DISPATCHER")
logger.setLevel(logging.INFO)

# Redis for deduplication
r = redis.Redis()

# Redis key for processed messages
DEDUP_KEY = "processed_fsm_msgs"

def is_duplicate(msg_id: str) -> bool:
    """Check if message ID has already been processed."""
    return r.sismember(DEDUP_KEY, msg_id)

def mark_processed(msg_id: str):
    """Mark message ID as processed."""
    r.sadd(DEDUP_KEY, msg_id)

def dispatch_command(message: dict):
    """
    Validate and dispatch FSM command.
    Expected message format:
    {
        "msg_id": str,
        "cmd": str,
        "params": dict,
        "sender": str,
        "version": str,
        "timestamp": str
    }
    """
    msg_id = message.get("msg_id")
    cmd = message.get("cmd")
    params = message.get("params", {})

    if not msg_id or not cmd:
        logger.warning("Missing msg_id or cmd in message.")
        return

    if is_duplicate(msg_id):
        logger.info(f"Duplicate message {msg_id} skipped.")
        return

    if not validate_message(message):
        logger.warning(f"Invalid message format: {message}")
        return

    try:
        logger.info(f"Dispatching command '{cmd}' with params {params}")
        # FSM command routing
        if cmd == "reset_fsm":
            fsm.reset(reason=params.get("reason", "unspecified"))
        elif cmd == "vers":
            fsm.version_check(params.get("version"))
        elif cmd == "ping":
            fsm.ping()
        elif cmd == "init":
            fsm.initialize(params)
        elif cmd == "status":
            fsm.report_status()
        else:
            logger.warning(f"Unknown command '{cmd}'")
            return

        mark_processed(msg_id)

    except Exception as e:
        logger.error(f"Error dispatching command '{cmd}': {e}")

