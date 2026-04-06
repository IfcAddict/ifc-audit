bl_info = {
    "name": "IFC Audit",
    "author": "IfcAddict (Adaptation) + AGR Digital Building (Base Logic)",
    "version": (0, 2, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > IFC",
    "description": "Audit, inspect, navigate and export IFC issues in Blender + Bonsai",
    "category": "BIM",
}

try:
    import bpy
    from .blender.props import classes as props_classes, register_props, unregister_props
    from .blender.operators import classes as operator_classes
    from .blender.panel import classes as panel_classes
    from .blender.preferences import classes as preference_classes
    _BLENDER_AVAILABLE = True
    classes = [*preference_classes, *props_classes, *operator_classes, *panel_classes]
except ImportError:
    _BLENDER_AVAILABLE = False
    classes = []

from .core.logger import setup_logger

def register():
    if not _BLENDER_AVAILABLE:
        return
    setup_logger() # Initialize the logging system
    for cls in classes:
        bpy.utils.register_class(cls)
    register_props()

def unregister():
    if not _BLENDER_AVAILABLE:
        return
    unregister_props()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
