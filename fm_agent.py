from cayley.protocol_spec import PROTOCOL_VERSION, version_cmp

class AgentFSM:
    def __init__(self):
        self.state = "idle"
        self.version = None

    def handle_event(self, event, params):
        if event == "vers":
            client_version = params.get("version")
            cmp = version_cmp(client_version, PROTOCOL_VERSION)

            if cmp == 0:
                self.version = client_version
                self.state = "esta"
                return {
                    "status": "OK",
                    "result": {
                        "state": self.state,
                        "version": self.version
                    }
                }
            else:
                self.version = None
                self.state = "idle"
                return {
                    "status": "VERSION_MISMATCH",
                    "result": {
                        "expected": PROTOCOL_VERSION,
                        "received": client_version,
                        "cmp": cmp,
                        "transition": "reset_to_idle",
                        "state": self.state
                    }
                }

        if self.state != "esta":
            return {
                "status": "REJECTED",
                "result": {
                    "reason": f"Event '{event}' not allowed in state '{self.state}'",
                    "state": self.state
                }
            }

        if event == "purge":
            return self._handle_purge(params)

        return {
            "status": "REJECTED",
            "result": {
                "reason": f"Unknown event '{event}'",
                "state": self.state
            }
        }

    def _handle_purge(self, params):
        # Beispielhafte Purge-Logik – hier nur symbolisch
        purged = []
        for text in list(bpy.data.texts):
            if text.name != "agent_zmq.py":
                bpy.data.texts.remove(text)
                purged.append(text.name)
        return {
            "status": "OK",
            "result": {
                "purged": purged,
                "count": len(purged),
                "state": self.state
            }
        }

    def get_status(self):
        return {
            "state": self.state,
            "version": self.version
        }

#======
__meta__ = {
    "name": "cayley.fm_agent",
    "requires": ["protocol_spec", "trace_utils"],
    "provides": ["AgentFSM"],
    "resources": []
}

from cayley.module_registry import register_meta
register_meta(__meta__)
#=====



