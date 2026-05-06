from __future__ import annotations
import bpy

class IFCIssueItem(bpy.types.PropertyGroup):
    ifc_id: bpy.props.IntProperty(default=-1)
    name: bpy.props.StringProperty(default="")
    issue_type: bpy.props.StringProperty(default="")
    description: bpy.props.StringProperty(default="")
    payload_index: bpy.props.IntProperty(default=-1)
    is_group: bpy.props.BoolProperty(default=False)
    is_expanded: bpy.props.BoolProperty(default=False)
    parent_id: bpy.props.IntProperty(default=-1)
    level: bpy.props.IntProperty(default=0)

class IFCAuditorProperties(bpy.types.PropertyGroup):
    use_active_ifc: bpy.props.BoolProperty(
        name="Use active IFC in memory",
        description="If checked, uses the model currently loaded in Bonsai. If unchecked, uses the file below",
        default=True
    )
    filepath: bpy.props.StringProperty(name="IFC File Path", subtype='FILE_PATH', default="")
    status: bpy.props.StringProperty(name="Status", default="Ready")
    has_audit_cache: bpy.props.BoolProperty(name="Tiene Caché", default=False)
    issue_filter: bpy.props.EnumProperty(
        name="Filter",
        items=[
            ("all", "All", "Show all issues"),
            ("orphans", "Orphans", "Show orphans"),
            ("empty_psets", "Empty PSets", "Show empty property sets"),
            ("unused_types", "Unused Types", "Show unused types"),
            ("duplicate_guids", "Duplicate GUIDs", "Show duplicate GlobalIds"),
            ("missing_properties", "Missing Properties", "Show missing properties"),
            ("heavy_brep", "Heavy BRep", "Show heavy BRep geometry"),
        ],
        default="all",
    )

    total_entities: bpy.props.IntProperty(default=0)
    total_issues: bpy.props.IntProperty(default=0)
    empty_psets: bpy.props.IntProperty(default=0)
    orphans: bpy.props.IntProperty(default=0)
    unused_types: bpy.props.IntProperty(default=0)
    duplicate_guids: bpy.props.IntProperty(default=0)
    missing_props: bpy.props.IntProperty(default=0)
    heavy_brep: bpy.props.IntProperty(default=0)

    clean_empty_psets: bpy.props.BoolProperty(name="Remove empty PropertySets", default=True)
    clean_unused_types: bpy.props.BoolProperty(name="Remove unused types", default=True)

AUDIT_CACHE = {}
UI_FLAT_LIST = []

classes = [IFCIssueItem, IFCAuditorProperties]

def register_props():
    bpy.types.Scene.ifc_auditor_props = bpy.props.PointerProperty(type=IFCAuditorProperties)
    bpy.types.Scene.ifc_auditor_issues = bpy.props.CollectionProperty(type=IFCIssueItem)
    bpy.types.Scene.ifc_auditor_issues_index = bpy.props.IntProperty(default=0)

def unregister_props():
    del bpy.types.Scene.ifc_auditor_props
    del bpy.types.Scene.ifc_auditor_issues
    del bpy.types.Scene.ifc_auditor_issues_index
