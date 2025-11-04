# module_info.py

import os
import hashlib
import importlib.util

def resolve_module_info(name: str) -> dict:
    spec = importlib.util.find_spec(name)
    path = spec.origin if spec and spec.origin else "unknown"
    status = "loaded" if spec else "missing"
    mod_type = "builtin"

    if path != "unknown":
        abspath = os.path.abspath(path)
        dirname = os.path.dirname(abspath)
        basename = os.path.basename(abspath)
        init_path = os.path.join(dirname, "__init__.py")
        mod_type = "package" if os.path.isfile(init_path) else "standalone"
        if ".zip" in abspath:
            mod_type = "zip"
    else:
        abspath = "n/a"
        dirname = ""
        basename = ""

    parts = name.split(".")
    cluster = ".".join(parts[:3]) if len(parts) >= 3 else ".".join(parts[:2]) if len(parts) >= 2 else parts[0]

    return {
        "name": name,
        "status": status,
        "mod_type": mod_type,
        "file": abspath,
        "dir": dirname,
        "base": basename,
        "cluster": cluster,
        "file_hash": hash_file(abspath) if path != "unknown" else "missing"
    }

def hash_file(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return "missing"

def scan_sysmodules():
    import sys
    modules = []
    for name in sys.modules:
        if name == "__main__":
            continue
        try:
            modules.append(resolve_module_info(name))
        except Exception as e:
            print(f"[warn] Skipped {name}: {e}")
    return modules

