import json
import logging
import uuid
from datetime import datetime
from confluent_kafka import Producer
from cayley.fsm_protocol import get_protocol_version

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FSM_MANAGER")

# Kafka Producer-Konfiguration
producer = Producer({
   #"bootstrap.servers": "localhost:9092",      # Cluster WSL
    "bootstrap.servers": "172.31.20.147:9092",  # Cluster WSL
    "client.id": "fsm-manager",
    "linger.ms": 10
})

# Default-Kontext
TOPIC = "fsm.commands"
SENDER = "fsm_manager"

def generate_msg_id() -> str:
    return str(uuid.uuid4())

def now_iso() -> str:
    return datetime.utcnow().isoformat()

def send_command(cmd: str, params: dict = None, reply_to: str = None):
    """
    Sendet ein FSM-Kommando als Kafka-Message.
    """
    msg = {
        "msg_id": generate_msg_id(),
        "cmd": cmd,
        "params": params or {},
        "sender": SENDER,
        "version": get_protocol_version(),
        "timestamp": now_iso()
    }

    if reply_to:
        msg["reply_to"] = reply_to

    payload = json.dumps(msg).encode("utf-8")

    def delivery_report(err, msg):
        if err is not None:
            logger.error(f"Delivery failed for {msg.key()}: {err}")
        else:
            logger.info(f"Command '{cmd}' sent to {msg.topic()} [{msg.partition()}] offset {msg.offset()}")

    producer.produce(topic=TOPIC, value=payload, callback=delivery_report)
    producer.poll(0)

def flush():
    producer.flush()

# Beispielkommandos
if __name__ == "__main__":
    send_command("ping")
    send_command("reset_fsm", {"reason": "manual test"})
    send_command("init", {"config": "default"})
    send_command("status")
    flush()

