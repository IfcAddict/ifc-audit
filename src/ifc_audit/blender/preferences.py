from __future__ import annotations
import bpy

class IFCAuditorPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__.split(".")[0]

    ghost_alpha: bpy.props.FloatProperty(
        name="Ghost transparency",
        description="Opacity reduction applied to non-selected objects when focusing an issue",
        default=0.85,
        min=0.0,
        max=1.0,
    )

    ghost_color: bpy.props.FloatVectorProperty(
        name="Ghost color",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(0.80, 0.80, 0.80),
    )

    color_orphans: bpy.props.FloatVectorProperty(
        name="Orphans",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.00, 0.30, 0.30),
    )

    color_empty_psets: bpy.props.FloatVectorProperty(
        name="Empty PropertySets",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.00, 0.60, 0.20),
    )

    color_unused_types: bpy.props.FloatVectorProperty(
        name="Unused types",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(0.30, 0.60, 1.00),
    )

    color_duplicate_guids: bpy.props.FloatVectorProperty(
        name="Duplicate GUIDs",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.00, 0.20, 1.00),
    )

    color_missing_properties: bpy.props.FloatVectorProperty(
        name="Missing properties",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.00, 1.00, 0.20),
    )

    color_brep_very_high: bpy.props.FloatVectorProperty(
        name="Heavy BRep very high",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.00, 0.00, 0.00),
    )

    color_brep_high: bpy.props.FloatVectorProperty(
        name="Heavy BRep high",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.00, 0.75, 0.00),
    )

    color_brep_medium: bpy.props.FloatVectorProperty(
        name="Heavy BRep medium",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(0.00, 0.00, 0.00),
    )

    color_brep_low: bpy.props.FloatVectorProperty(
        name="Heavy BRep low",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(0.00, 1.00, 0.00),
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Ghost mode")
        layout.prop(self, "ghost_alpha")
        layout.prop(self, "ghost_color")
        layout.separator()
        layout.label(text="Highlight colors by issue type")
        col = layout.column(align=True)
        col.prop(self, "color_orphans")
        col.prop(self, "color_empty_psets")
        col.prop(self, "color_unused_types")
        col.prop(self, "color_duplicate_guids")
        col.prop(self, "color_missing_properties")
        layout.separator()
        layout.label(text="Heavy BRep colors by range")
        col = layout.column(align=True)
        col.prop(self, "color_brep_very_high")
        col.prop(self, "color_brep_high")
        col.prop(self, "color_brep_medium")
        col.prop(self, "color_brep_low")

classes = [IFCAuditorPreferences]
