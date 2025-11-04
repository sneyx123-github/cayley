# ----------------------------------------
# FSM-Spezifikation (extern definiert)
# ----------------------------------------

modFSM_spec_test1 = {
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

modFSM_spec_prelife = {
    "unset": {
        "load": {
            "next": "active",
            "actions": [
                {"type": "call", "name": "initialize_module"},
                {"type": "send", "target": "manager", "event": "ready", "params": {"module": "$name"}}
            ]
        },
        "fail": {
            "next": "error",
            "actions": [
                {"type": "call", "name": "log_failure"}
            ]
        }
    },
    "error": {
        "retry": {
            "condition": "context['retry_count'] < 3",
            "next": "unset",
            "actions": [
                {"type": "call", "name": "reset_module"}
            ]
        }
    },
    "active": {
        "unload": {
            "next": "terminated",
            "actions": [
                {"type": "call", "name": "release_resources"},
                {"type": "send", "target": "manager", "event": "terminated", "params": {"module": "$name"}}
            ]
        }
    }
}

