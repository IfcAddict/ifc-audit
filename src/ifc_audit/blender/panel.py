from __future__ import annotations
import bpy

ICON_MAP = {
    "orphans": 'ERROR',
    "empty_psets": 'TRASH',
    "unused_types": 'OUTLINER_OB_GROUP_INSTANCE',
    "duplicate_guids": 'DUPLICATE',
    "missing_properties": 'QUESTION',
    "heavy_brep": 'MESH_ICOSPHERE',
}

LABEL_MAP = {
    "orphans": "Orphan",
    "empty_psets": "Empty PSet",
    "unused_types": "Unused Type",
    "duplicate_guids": "Duplicate GUID",
    "missing_properties": "Missing Properties",
    "heavy_brep": "Heavy BRep",
}

class IFC_UL_issue_list(bpy.types.UIList):
    bl_idname = "IFC_UL_issue_list"

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        flags = []
        for i, item in enumerate(items):
            show = True
            if item.level > 0:
                parent = items[item.parent_id] if 0 <= item.parent_id < len(items) else None
                show = bool(parent and parent.is_expanded)
            flags.append(self.bitflag_filter_item if show else 0)
        return flags, []

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index=0, flt_flag=0):
        row = layout.row(align=True)

        if item.level > 0:
            row.separator(factor=2.0)

        if item.is_group:
            icon_name = 'TRIA_DOWN' if item.is_expanded else 'TRIA_RIGHT'
            op = row.operator("ifc_auditor.toggle_group", text="", icon=icon_name, emboss=False)
            op.index = index
            row.label(text="", icon=ICON_MAP.get(item.issue_type, 'DOT'))
            col = row.column(align=True)
            col.label(text=item.name or "Grupo")
            col.label(text=item.description or LABEL_MAP.get(item.issue_type, item.issue_type), icon='BLANK1')
        else:
            row.label(text="", icon=ICON_MAP.get(item.issue_type, 'DOT'))
            col = row.column(align=True)
            col.label(text=item.name or "Sin nombre")
            col.label(text=item.description or LABEL_MAP.get(item.issue_type, item.issue_type), icon='BLANK1')

class IFC_PT_auditor_panel(bpy.types.Panel):
    bl_label = "IFC Audit v0.2.1"
    bl_idname = "IFC_PT_auditor_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'IFC'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.ifc_auditor_props

        box = layout.box()
        box.label(text="Model Source", icon='WORLD_DATA')
        box.prop(props, "use_active_ifc")
        if not props.use_active_ifc:
            box.prop(props, "filepath", text="Select IFC File")
        
        box.operator("ifc_auditor.run_audit", icon='VIEWZOOM')

        box = layout.box()
        box.label(text="Summary")
        col = box.column(align=True)
        col.label(text=f"Entities: {props.total_entities}")
        col.label(text=f"Issues: {props.total_issues}")
        col.label(text=f"Empty Psets: {props.empty_psets}")
        col.label(text=f"Orphans: {props.orphans}")
        col.label(text=f"Unused types: {props.unused_types}")
        col.label(text=f"Duplicate GUIDs: {props.duplicate_guids}")
        col.label(text=f"Missing properties: {props.missing_props}")
        col.label(text=f"Heavy BRep: {props.heavy_brep}")

        box = layout.box()
        box.label(text="Filter issues by type")
        row = box.row(align=True)
        op = row.operator("ifc_auditor.show_issue_category", text="All")
        op.category = "all"
        op = row.operator("ifc_auditor.show_issue_category", text="Orphans", icon='ERROR')
        op.category = "orphans"
        op = row.operator("ifc_auditor.show_issue_category", text="Psets", icon='TRASH')
        op.category = "empty_psets"

        row = box.row(align=True)
        op = row.operator("ifc_auditor.show_issue_category", text="Types", icon='OUTLINER_OB_GROUP_INSTANCE')
        op.category = "unused_types"
        op = row.operator("ifc_auditor.show_issue_category", text="GUIDs", icon='DUPLICATE')
        op.category = "duplicate_guids"
        op = row.operator("ifc_auditor.show_issue_category", text="Props", icon='QUESTION')
        op.category = "missing_properties"

        row = box.row(align=True)
        op = row.operator("ifc_auditor.show_issue_category", text="Heavy BRep", icon='MESH_ICOSPHERE')
        op.category = "heavy_brep"

        row = box.row(align=True)
        row.prop(props, "issue_filter", text="Active filter")
        row.operator("ifc_auditor.refresh_issue_list", text="", icon='FILE_REFRESH')

        box.template_list(
            "IFC_UL_issue_list",
            "",
            scene,
            "ifc_auditor_issues",
            scene,
            "ifc_auditor_issues_index",
            rows=10,
        )

        row = box.row(align=True)
        row.operator("ifc_auditor.select_active_issue", text="Go to issue", icon='RESTRICT_SELECT_OFF')
        row.operator("ifc_auditor.select_all_listed_issues", text="Select all", icon='UV_SYNC_SELECT')
        row = box.row(align=True)
        row.operator("ifc_auditor.reset_visual", text="Reset Visualization", icon='HIDE_OFF')

        box = layout.box()
        box.label(text="Export & cleanup")
        box.prop(props, "clean_empty_psets")
        box.prop(props, "clean_unused_types")
        row = box.row(align=True)
        row.operator("ifc_auditor.export_report", icon='TEXT', text="JSON")
        row.operator("ifc_auditor.export_html_report", icon='FILE_TEXT', text="HTML Report")
        row.operator("ifc_auditor.export_clean_copy", icon='FILE_TICK', text="Clean IFC")

        layout.separator()
        layout.label(text=f"Status: {props.status}", icon='INFO')

classes = [IFC_UL_issue_list, IFC_PT_auditor_panel]
