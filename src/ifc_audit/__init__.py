bl_info = {
    "name": "IFC Audit",
    "author": "IfcAddict (Adaptation) + AGR Digital Building (Base Logic)",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > IFC",
    "description": "Audit, inspect, navigate and export IFC issues in Blender + Bonsai",
    "category": "BIM",
}

import bpy

from .blender.props import classes as props_classes, register_props, unregister_props
from .blender.operators import classes as operator_classes
from .blender.panel import classes as panel_classes
from .blender.preferences import classes as preference_classes

classes = [*preference_classes, *props_classes, *operator_classes, *panel_classes]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_props()


def unregister():
    unregister_props()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
