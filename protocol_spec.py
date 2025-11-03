# Aktuelle Protokollversion
PROTOCOL_VERSION = "1.0.0"

# Unterstützte Befehle mit Parametern und erlaubten Zuständen
SUPPORTED_COMMANDS = {
    "vers": {
        "params": {
            "MAND": ["version"],
            "OPT": []
        },
        "allowed_states": ["idle", "esta"]
    },
    "purge": {
        "params": {
            "MAND": [],
            "OPT": ["scope", "dry_run"]
        },
        "allowed_states": ["esta"]
    },
    "fsm_status": {
        "params": {
            "MAND": [],
            "OPT": []
        },
        "allowed_states": ["idle", "esta"]
    }
}

# SemVer-kompatibler Versionsvergleich
def parse_version(v):
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except:
        return (0, 0, 0)

def version_cmp(a, b):
    va = parse_version(a)
    vb = parse_version(b)
    if va < vb:
        return -1
    elif va > vb:
        return 1
    else:
        return 0

def is_version_compatible(v):
    return version_cmp(v, PROTOCOL_VERSION) == 0

def get_protocol_info():
    return {
        "version": PROTOCOL_VERSION,
        "commands": list(SUPPORTED_COMMANDS.keys()),
        "structure": SUPPORTED_COMMANDS
    }

def validate_params(cmd, params):
    spec = SUPPORTED_COMMANDS.get(cmd)
    if not spec:
        return False, f"Unknown command '{cmd}'"

    mand = set(spec["params"].get("MAND", []))
    opt = set(spec["params"].get("OPT", []))
    allowed = mand | opt
    received = set(params.keys())

    missing = list(mand - received)
    unexpected = list(received - allowed)

    if missing:
        return False, f"Missing mandatory parameters: {missing}"
    if unexpected:
        return False, f"Unexpected parameters: {unexpected}"

    return True, "OK"

#======
__meta__ = {
    "name": "cayley.protocol_spec",
    "requires": ["trace_utils"],
    "provides": ["ProtocolSpec"],
    "resources": []
}

from cayley.module_registry import register_meta
register_meta(__meta__)
#=====



