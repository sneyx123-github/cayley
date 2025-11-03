import json
import os


REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "module_registry.json")
_registry = {}

#-----
if 1:
    print("module_registry.py: REGISTRY_PATH=", REGISTRY_PATH)
#-----

def register_meta(meta):
    name = meta.get("name")
    if not name:
        raise ValueError("Meta must include 'name'")
    _registry[name] = meta
    _save_registry()

def unregister_meta(name):
    if name in _registry:
        del _registry[name]
        _save_registry()

def get_registry():
    return dict(_registry)

def _save_registry():
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(_registry, f, indent=2)

def load_registry():
    global _registry
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            _registry = json.load(f)


#======
__meta__ = {
    "name": "module_registry",
    "requires": ["module_registry", "trace_utils"],
    "provides": [],
    "resources": []
}

#from cayley.module_registry import register_meta
register_meta(__meta__)
#=====

