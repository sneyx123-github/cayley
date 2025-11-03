# ----------------------------------------
# FSM-Spezifikation (extern definiert)
# ----------------------------------------
# Beispielstruktur:

modFSM_spec = {
    "active": {
        "unload": {
            "condition": "params['error_level'] < 3",
            "next": "terminated",
            "actions": [
                {"type": "call", "name": "release_resources"},
                {"type": "send", "target": "manager", "event": "reset", "params": {"reason": "unload"}}
            ]
        }
    }
}

