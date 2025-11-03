import zmq
import json
from cayley.protocol_spec import PROTOCOL_VERSION, parse_version
from cayley.trace_utils import log_trace

class ManagerDirector:
    def __init__(self, address="tcp://localhost:5555", timeout=1000):
        log_trace("ManagerDirector initializing", who="MGR")
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(address)
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        self.timeout = timeout
        log_trace("ManagerDirector initialized", who="MGR")

    def send(self, cmd, params=None):
        if params is None:
            params = {}
        try:
            self.socket.send_json({"cmd": cmd, "params": params})
            socks = dict(self.poller.poll(self.timeout))
            if socks.get(self.socket) == zmq.POLLIN:
                reply = self.socket.recv_json()
                log_trace(f"{cmd} → {reply.get('status')}", who="MGR")
                return reply
            else:
                log_trace(f"{cmd} → TIMEOUT", who="MGR")
                return {"status": "TIMEOUT", "result": {"reason": "No response"}}
        except Exception as e:
            log_trace(f"{cmd} → ERROR: {e}", who="MGR")
            return {"status": "ERROR", "result": {"error": str(e)}}

    # Core protocol events
    def vers(self, version=None):
        if version is None:
            version = PROTOCOL_VERSION
        return self.send("vers", {"version": version})

    def fsm_status(self):
        return self.send("fsm_status")

    def purge(self, scope=None, dry_run=None):
        params = {}
        if scope:
            params["scope"] = scope
        if dry_run is not None:
            params["dry_run"] = dry_run
        return self.send("purge", params)

    def unfold(self):
        return self.send("unfold", {})

    def fingerprint(self):
        return self.send("fingerprint", {})

    # Protocol conformance tests
    def test_unknown_event(self):
        return self.send("explode", {})

    def test_unknown_param(self):
        return self.send("vers", {"versoin": PROTOCOL_VERSION})  # typo intentional

    def test_missing_param(self):
        return self.send("vers", {})  # missing 'version'

    def test_disallowed_state(self):
        return self.send("purge", {})  # only allowed in 'esta'

    def test_vers_incompatible(self):
        major, minor, patch = parse_version(PROTOCOL_VERSION)
        incompatible = f"{major}.{minor}.{patch + 1}"
        return self.vers(incompatible)


#======
__meta__ = {
    "name": "manager_director",
    "requires": ["protocol_spec", "trace_utils"],
    "provides": ["ManagerDirector"],
    "resources": []
}

from cayley.module_registry import register_meta
register_meta(__meta__)
#=====


