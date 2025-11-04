import threading
import zmq
#import bpy
import json
from cayley.protocol_spec import PROTOCOL_VERSION
from cayley.fm_agent import AgentFSM  # deine FSM-Klasse

class AgentController:
    def __init__(self):
        print("AgentController initializing")
        self.thread = None
        self.stop_event = threading.Event()
        self.fsm = AgentFSM()
        self.running = False
        print("AgentController initialized.")


    def start(self):
        if self.thread and self.thread.is_alive():
            print("Agent already running.")
            return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.run_agent, daemon=True)
        self.thread.start()
        self.running = True
        print("Agent started.")

    def stop(self):
        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join(timeout=2.0)
            self.running = False
            print("Agent stopped.")
        else:
            print("No running agent thread found.")

    def status(self):
        return {
            "running": self.running and self.thread and self.thread.is_alive(),
            "thread_alive": self.thread.is_alive() if self.thread else False,
            "fsm_state": self.fsm.get_status()
        }

    def run_agent(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5555")
        print("Agent ZMQ listening on tcp://*:5555")

        while not self.stop_event.is_set():
            try:
                msg = socket.recv_json(flags=zmq.NOBLOCK)
                cmd = msg.get("cmd")
                params = msg.get("params", {})
                response = self.fsm.handle_event(cmd, params)
                socket.send_json(response)
            except zmq.Again:
                continue
            except Exception as e:
                socket.send_json({
                    "status": "ERROR",
                    "result": {
                        "error": str(e)
                    }
                })

        socket.close()
        context.term() 
        print("Agent ZMQ socket closed.")

#---
def agent_ctl():
    import bpy

    if 0:
        # Initialisierung (einmalig)
        bpy.app.driver_namespace["agent"] = AgentController()
    elif 0:
        # Starten
        bpy.app.driver_namespace["agent"].start()
    elif 0:
        # Status prüfen
        bpy.app.driver_namespace["agent"].status()
    elif 0:
        # Stoppen
        bpy.app.driver_namespace["agent"].stop()
    else:
        print("AgentController is UNATTENDED")

#------
#
# "provides": ["AgentController", "FSM_AGENT", "PROTOCOL_VERSION"]
#
# "provides": {
#     "classes": ["AgentController"],
#     "fsm": ["AgentFSM"],
#     "constants": ["PROTOCOL_VERSION"]
# }
# 
#------
#======
__meta__ = {
    "name": "cayley.agent_controller",
    "requires": ["protocol_spec", "trace_utils"],
	"provides": ["AgentController", "AgentFSM", "PROTOCOL_VERSION"],
    "resources": ["thread:agent", "socket:tcp://*:5555"]
}

from cayley.module_registry import register_meta
register_meta(__meta__)
#=====


