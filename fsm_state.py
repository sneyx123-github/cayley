import logging
from datetime import datetime

# Setup logging
logger = logging.getLogger("FSM_STATE")
logger.setLevel(logging.INFO)

class FSM:
    def __init__(self):
        self.state = "idle"
        self.version = "1.0.0"
        self.last_updated = datetime.utcnow()
        self.initialized = False
        logger.info("FSM initialized.")

    def reset(self, reason="unspecified"):
        logger.warning(f"FSM reset triggered. Reason: {reason}")
        self.state = "idle"
        self.initialized = False
        self.last_updated = datetime.utcnow()

    def ping(self):
        logger.info("FSM ping received.")
        print({
            "status": "alive",
            "state": self.state,
            "version": self.version,
            "timestamp": self.last_updated.isoformat()
        })

    def version_check(self, peer_version):
        if peer_version != self.version:
            logger.warning(f"Version mismatch: peer={peer_version}, local={self.version}")
        else:
            logger.info(f"Version match confirmed: {self.version}")

    def initialize(self, params):
        logger.info(f"FSM initializing with params: {params}")
        self.state = "ready"
        self.initialized = True
        self.last_updated = datetime.utcnow()

    def report_status(self):
        status = {
            "state": self.state,
            "version": self.version,
            "initialized": self.initialized,
            "timestamp": self.last_updated.isoformat()
        }
        logger.info(f"FSM status: {status}")
        print(status)

# Singleton instance
fsm = FSM()

