import json
import logging
import redis
from uuid import uuid4
from datetime import datetime
# Both libraries have dfferent Consumer with different ecurity_protocol defaults
#from gcn_kafka import Consumer
from confluent_kafka import Consumer

from cayley.fsm_dispatcher import dispatch_command
from cayley.fsm_protocol import validate_message

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FSM_AGENT")

if 0: # Redis for deduplication
    r = redis.Redis()

# Kafka consumer setup
#----
if 0:
    consumer = Consumer(
        username='your_username',
        password='your_password',
        bootstrap_servers='gcn.nasa.gov:9092',
        security_protocol='SASL_SSL',
        sasl_mechanism='PLAIN'
    )

elif 0:
    consumer = Consumer({
        "bootstrap.servers": "172.31.20.147:9092",
        "security.protocol": "SASL_SSL",
        "sasl.mechanism": "PLAIN",
        "sasl.username": "your_username",
        "sasl.password": "your_password",
        "group.id": "fsm-agent-group",
        "auto.offset.reset": "earliest"
    })
elif 0:
    consumer = Consumer({
        #"bootstrap_servers":"172.31.20.147:9092",
        "client_id":"fsm-agent",
        #"client_id":"XXXXXXXXXXXXXXXXXXXXXXXXX",
        #"client_secret":"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "linger.ms":10
    })
elif 1:
    consumer = Consumer({
        "bootstrap.servers": "172.31.20.147:9092",
        "group.id": "fsm-agent",
        "auto.offset.reset": "earliest"
    })

#----

# Subscribe to FSM command topic
consumer.subscribe(['fsm.commands'])

if 0: # Redis avail?
    def is_duplicate(msg_id: str) -> bool:
        return r.sismember("processed_fsm_msgs", msg_id)

    def mark_processed(msg_id: str):
        r.sadd("processed_fsm_msgs", msg_id)

def process_message(message):
    try:
        if 0:                           # bytes
            value = message.value()
        else:                           # json
            value = json.loads(message.value().decode("utf-8"))
        if 0:   # Decode Received message
            logger.error(f"CP1")
            logger.error(value)

        msg_id = value.get("msg_id") or str(message.offset())

        if 0:                           # Redis in framework required
            if is_duplicate(msg_id):
                logger.info(f"Duplicate message {msg_id} skipped.")
                return

        if not validate_message(value):
            logger.warning(f"Invalid message format: {value}")
            return

        logger.info(f"Processing FSM command: {value['cmd']} from {value['sender']}")
        dispatch_command(value)
        if 0: # Redis avail?
            mark_processed(msg_id)

    except Exception as e:
        logger.error(f"Error processing message: {e}")

def run_agent():
    logger.info("FSM Agent started.")
    while True:
        for message in consumer.consume(timeout=1):
            if message.error():
                logger.error(f"Kafka error: {message.error()}")
                continue
            process_message(message)

if __name__ == "__main__":
    run_agent()

