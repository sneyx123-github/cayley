import json
import os
import hashlib

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "module_registry.json")
_registry = None
_registry_hash = None

def _trace(msg):
    try:
        import trace_utils
        trace_utils.trace(msg)
    except ImportError:
        print("[trace]", msg)

def _ensure_loaded():
    global _registry, _registry_hash
    if _registry is None:
        if os.path.exists(REGISTRY_PATH):
            try:
                with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                    content = f.read()
                    _registry = json.loads(content)
                    _registry_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                    _trace("Registry loaded from disk.")
            except Exception as e:
                _trace(f"Registry load failed: {e}")
                _registry = {}
                _registry_hash = None
        else:
            _registry = {}
            _registry_hash = None

def _check_integrity():
    """Detect unauthorized changes to the registry file."""
    if not os.path.exists(REGISTRY_PATH):
        return False
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            current_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            return current_hash == _registry_hash
    except Exception as e:
        _trace(f"Integrity check failed: {e}")
        return False

def register_meta(meta):
    _ensure_loaded()
    name = meta.get("name")
    if not name:
        raise ValueError("Meta must include 'name'")
    _registry[name] = meta
    _save_registry()
    _trace(f"Meta registered: {name}")

def unregister_meta(name):
    _ensure_loaded()
    if name in _registry:
        del _registry[name]
        _save_registry()
        _trace(f"Meta unregistered: {name}")

def get_registry():
    _ensure_loaded()
    if not _check_integrity():
        _trace("WARNING: Registry file has been modified externally.")
    return dict(_registry)

def _save_registry():
    _ensure_loaded()
    try:
        content = json.dumps(_registry, indent=2)
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        global _registry_hash
        _registry_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        _trace("Registry saved to disk.")
    except Exception as e:
        _trace(f"Registry save failed: {e}")

def init_registry(force=False):
    global _registry, _registry_hash
    if force or not os.path.exists(REGISTRY_PATH):
        _registry = {}
        _save_registry()
        _trace("Registry initialized.")
    else:
        _ensure_loaded()

#======
__meta__ = {
    "name": "module_registry",
    "requires": ["trace_utils"],
    "provides": ["register_meta", "unregister_meta", "get_registry", "init_registry"],
    "resources": ["module_registry.json"]
}

register_meta(__meta__)
#======

