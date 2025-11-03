"""
Mypack module mypack.__main__ 
It could be evaluated by: ipython -i -m mypack ...

"""

#======
__meta__ = {
    "name": "cayley.__main__",
    "requires": ["module_registry", "trace_utils"],
    "provides": [],
    "resources": []
}

from cayley.module_registry import register_meta
register_meta(__meta__)
#=====

if(__name__=='__main__'):
    print('cayley.__main__: evaluation')
    print(f'{__name__}: evaluation')

################################################################################
#   EOF
################################################################################
