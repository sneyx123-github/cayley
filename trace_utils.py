import datetime
import inspect
import os

#======
__meta__ = {
    "name": "trace_utils",
    "requires": [],
    "provides": [],
    "resources": []
}

from cayley.module_registry import register_meta
register_meta(__meta__)
#=====

def log_trace(msg, who=None):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    frame = inspect.stack()[1]
    filename = os.path.basename(frame.filename)
    funcname = frame.function

    # Fixe Breite: 20 Zeichen für filename und funcname, 4 für who
    filename_fmt = f"{filename:<20.20}"
    funcname_fmt = f"{funcname:<20.20}"
    who_fmt = f"{(who or ''):<4.4}"

    prefix = f"[{now}] {filename_fmt}::{funcname_fmt} [{who_fmt}]"
    print(f"{prefix} → {msg}")
