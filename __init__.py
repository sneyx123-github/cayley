#
# cayley/__init__.py
# this file can be empty or not
#
"""
This is cayley the toplevel package with some modules and subordinate packages.
There will be extensions support in the future.
"""

#
# list of modules of the package:
#
__all__ = [
    "fm_agent",
    "agent_controller",
    "manager_director",
    "protocol_spec",
    "trace_utils",
    "modmgr_ui",

    "module_registry",
    "__main__",
    "__init__",
    ]

#======
__meta__ = {
    "name": "__init__",
    "requires": ["module_registry", "trace_utils"],
    "provides": [],
    "resources": []
}

from cayley.module_registry import register_meta
register_meta(__meta__)
#=====

print('cayley.__main__: evaluation')
print(f'{__name__}: evaluation')

