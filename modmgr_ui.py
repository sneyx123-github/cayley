import bpy
from bpy.types import NodeTree, Node, NodeSocket, Operator
from bpy.props import StringProperty
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories

# NodeTree-Typ
class ModuleNodeTree(NodeTree):
    bl_idname = "ModuleNodeTreeType"
    bl_label = "Module Dependency Tree"
    bl_icon = "NODETREE"

# Socket-Typ
class ModuleSocket(NodeSocket):
    bl_idname = "ModuleSocketType"
    bl_label = "Module Socket"

    socket_type: StringProperty()

    def draw(self, context, layout, node, text):
        layout.label(text=self.socket_type)

    def draw_color(self, context, node):
        return (0.4, 0.6, 1.0, 1.0)

#((((
# Node-Typ
if 0:
    class ModuleNode(Node):
        bl_idname = "ModuleNodeType"
        bl_label = "Module"

        module_name: StringProperty(name="Module Name")
        status: StringProperty(name="Status", default="unknown")

        @classmethod
        def poll(cls, ntree):
            return ntree.bl_idname == "ModuleNodeTreeType"

        def init(self, context):
            self.inputs.new("ModuleSocketType", "Requires").socket_type = "requires"
            self.outputs.new("ModuleSocketType", "Provides").socket_type = "provides"
            self.outputs.new("ModuleSocketType", "Resources").socket_type = "resources"

        def draw_buttons(self, context, layout):
            layout.prop(self, "module_name")
            layout.label(text=f"Status: {self.status}")
            op = layout.operator("module.reload", text="Reload")
            op.module = self.module_name
else:
    import bpy
    from bpy.types import Node
    from bpy.props import StringProperty
    from cayley.module_registry import get_registry

    class ModuleNode(Node):
        bl_idname = "ModuleNodeType"
        bl_label = "Module Node"
        bl_icon = "NODE"

        module_name: StringProperty(
            name="Module Name",
            update=lambda self, ctx: self.update_sockets()
        )

        status: StringProperty(name="Status", default="unknown")
        label: StringProperty(name="Label", default="")

        def init(self, context):
            self.build_sockets()

        def build_sockets(self):
            self.inputs.clear()
            self.outputs.clear()

            meta = get_registry().get(self.module_name, {})
            if not meta:
                return

            # Eingänge für requires
            for req in meta.get("requires", []):
                sock = self.inputs.new("ModuleSocketType", req)
                sock.socket_type = "requires"

            # Ausgänge für provides
            provides = meta.get("provides", [])
            if isinstance(provides, dict):
                for typ, symbols in provides.items():
                    for sym in symbols:
                        sock = self.outputs.new("ModuleSocketType", sym)
                        sock.socket_type = f"provides:{typ}"
            else:
                for sym in provides:
                    sock = self.outputs.new("ModuleSocketType", sym)
                    sock.socket_type = "provides"

            # Ausgänge für resources
            for res in meta.get("resources", []):
                sock = self.outputs.new("ModuleSocketType", res)
                sock.socket_type = "resource"

        def update_sockets(self):
            self.build_sockets()
#))))


# Operator
class MODULE_OT_reload(Operator):
    bl_idname = "module.reload"
    bl_label = "Reload Module"

    module: StringProperty()

    def execute(self, context):
        import importlib
        try:
            mod = importlib.import_module(f"cayley.{self.module}")
            importlib.reload(mod)
            if hasattr(mod, "load"):
                mod.load()
            self.report({'INFO'}, f"Reloaded {self.module}")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}

# Node-Kategorie für Add-Menü
module_node_categories = [
    NodeCategory("MODULE_NODES", "Modules", items=[
        NodeItem("ModuleNodeType"),
    ])
]

# Registrierung
classes = [ModuleNodeTree, ModuleSocket, ModuleNode, MODULE_OT_reload]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_node_categories("MODULE_NODES", module_node_categories)

def unregister():
    unregister_node_categories("MODULE_NODES")
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
#-----
from cayley.module_registry import get_registry

def build_tree_from_registry(tree):
    registry = get_registry()
    nodes = {}
    spacing_x = 300
    spacing_y = 200
    col = 0

    # 1. Erzeuge Nodes aus Registry
    for i, (name, meta) in enumerate(registry.items()):
        node = tree.nodes.new("ModuleNodeType")
        node.module_name = name
        node.status = meta.get("status", "unknown")
        node.label = name
        node.location = (col * spacing_x, -i * spacing_y)
        nodes[name] = node

    # 2. Verlinke requires → target
    for name, meta in registry.items():
        source_node = nodes.get(name)
        for req in meta.get("requires", []):
            target_node = nodes.get(req)
            if source_node and target_node:
                tree.links.new(target_node.outputs.get("Provides"), source_node.inputs.get("Requires"))

    # 3. Verlinke resources als Ausgänge
    for name, meta in registry.items():
        source_node = nodes.get(name)
        for res in meta.get("resources", []):
            res_node = tree.nodes.new("ModuleNodeType")
            res_node.module_name = res
            res_node.label = res
            res_node.status = "resource"
            res_node.location = (source_node.location[0] + spacing_x, source_node.location[1] - 50)
            tree.links.new(source_node.outputs.get("Resources"), res_node.inputs.get("Requires"))

#-----

if 0:
    register()

#======
__meta__ = {
    "name": "cayley.modmgr_ui",
    "requires": ["module_registry", "trace_utils"],
    "provides": ["register", "unregister", "build_tree_from_registry"],
    "resources": ["thread:agent", "socket:tcp://*:5555"]
}

from cayley.module_registry import register_meta
register_meta(__meta__)
#=====

