from __future__ import annotations

import json
import os

import bpy

from ..core.auditor import IFCAuditor
from ..core.rules import ISSUE_TITLES
from .selectors import select_ifc_ids, get_objects_from_ifc_ids
from ..core.highlight import apply_ghost_highlight, restore_visual
from ..core.logger import get_logger
from ..core.reporter import HTMLReporter
import webbrowser
from datetime import datetime
logger = get_logger()

def update_props_from_results(props, results):
    summary = results.get("summary", {})
    props.total_entities = summary.get("total_entities", 0)
    props.total_issues = summary.get("total_issues", 0)
    props.empty_psets = summary.get("empty_psets", 0)
    props.orphans = summary.get("orphans", 0)
    props.unused_types = summary.get("unused_types", 0)
    props.duplicate_guids = summary.get("duplicate_guids", 0)
    props.missing_props = summary.get("missing_properties", 0)
    props.heavy_brep = summary.get("heavy_brep", 0)
    
    from .props import AUDIT_CACHE
    AUDIT_CACHE.clear()
    AUDIT_CACHE.update(results)
    props.has_audit_cache = True

def _get_addon_prefs(context):
    addon_name = __package__.split('.')[0]
    addon = context.preferences.addons.get(addon_name)
    return addon.preferences if addon else None

def _visible_children_for_filter(issue_filter):
    if issue_filter == "all":
        return {"orphans", "empty_psets", "unused_types", "duplicate_guids", "missing_properties", "heavy_brep"}
    return {issue_filter}

def fill_ui_tree(context, results):
    scene = context.scene
    props = context.scene.ifc_auditor_props
    scene.ifc_auditor_issues.clear()

    issues = results.get("issues", {})
    allowed = _visible_children_for_filter(props.issue_filter)
    
    from .props import UI_FLAT_LIST
    UI_FLAT_LIST.clear()

    def add_leaf(name, issue_type, payload, ifc_id=-1, description="", level=0, is_group=False, parent_id=-1):
        row = scene.ifc_auditor_issues.add()
        row.ifc_id = int(ifc_id)
        row.name = name
        row.issue_type = issue_type
        row.description = description
        
        UI_FLAT_LIST.append(payload)
        row.payload_index = len(UI_FLAT_LIST) - 1
        
        row.is_group = is_group
        row.is_expanded = False
        row.parent_id = parent_id
        row.level = level
        return len(scene.ifc_auditor_issues) - 1

    # Flat categories
    for key in ["empty_psets", "unused_types", "duplicate_guids"]:
        if key not in allowed:
            continue
        for item in issues.get(key, []):
            desc = item.get("type", "")
            if key == "duplicate_guids":
                desc = f"{item.get('guid', '')} | {item.get('count', 0)} entities"
            add_leaf(
                name=item.get("name", ISSUE_TITLES.get(key, key)),
                issue_type=key,
                payload=item,
                ifc_id=item.get("id", -1),
                description=desc,
                level=0,
                is_group=False,
            )

    # Orphans grouped
    if "orphans" in allowed:
        for group in issues.get("orphans", []):
            parent_index = add_leaf(
                name=f"Orphans: {group['type']} ({len(group['elements'])})",
                issue_type="orphans",
                payload=group,
                description=f"{len(group['elements'])} elements",
                level=0,
                is_group=True,
            )
            for elem in group["elements"]:
                desc = elem["type"]
                sev = elem.get("severity", "")
                if sev:
                    desc = f"{elem['type']} | {sev}"
                add_leaf(
                    name=elem["name"],
                    issue_type="orphans",
                    payload=elem,
                    ifc_id=elem["id"],
                    description=desc,
                    level=1,
                    is_group=False,
                    parent_id=parent_index,
                )

    # Missing properties grouped
    if "missing_properties" in allowed:
        for group in issues.get("missing_properties", []):
            parent_index = add_leaf(
                name=f"Property: {group['property']} ({len(group['elements'])})",
                issue_type="missing_properties",
                payload=group,
                description=f"{len(group['elements'])} elements affected",
                level=0,
                is_group=True,
            )
            for elem in group["elements"]:
                add_leaf(
                    name=elem["name"],
                    issue_type="missing_properties",
                    payload=elem,
                    ifc_id=elem["id"],
                    description=elem["type"],
                    level=1,
                    is_group=False,
                    parent_id=parent_index,
                )

    # Heavy BRep grouped
    if "heavy_brep" in allowed:
        for group in issues.get("heavy_brep", []):
            parent_index = add_leaf(
                name=f"BRep {group['group']} ({len(group['elements'])})",
                issue_type="heavy_brep",
                payload=group,
                description=f"{len(group['elements'])} elementos",
                level=0,
                is_group=True,
            )
            for elem in group["elements"]:
                add_leaf(
                    name=f"{elem['name']} ({elem['faces']} faces)",
                    issue_type="heavy_brep",
                    payload=elem,
                    ifc_id=elem["id"],
                    description=elem["type"],
                    level=1,
                    is_group=False,
                    parent_id=parent_index,
                )

def refresh_issue_list(context):
    props = context.scene.ifc_auditor_props
    if not props.has_audit_cache:
        context.scene.ifc_auditor_issues.clear()
        return
    from .props import AUDIT_CACHE
    fill_ui_tree(context, AUDIT_CACHE)

class IFC_OT_run_audit(bpy.types.Operator):
    bl_idname = "ifc_auditor.run_audit"
    bl_label = "Run Audit"
    bl_description = "Runs the audit on the active IFC in Bonsai or, if not available, on the specified file"

    def execute(self, context):
        props = context.scene.ifc_auditor_props
        filepath = None
        if not props.use_active_ifc:
            filepath = bpy.path.abspath(props.filepath).strip()
            if not filepath or not os.path.exists(filepath):
                props.status = "Error: Invalid file path"
                logger.error(f"Operator run_audit: {props.status}")
                self.report({'ERROR'}, "Please specify a valid IFC file path")
                return {'CANCELLED'}

        try:
            auditor = IFCAuditor.from_bonsai_or_file(filepath)
            results = auditor.run()
            update_props_from_results(props, results)
            fill_ui_tree(context, results)
            props.status = f"Audit complete: {props.total_entities} entities, {props.total_issues} issues"
            logger.info(f"Operator run_audit: {props.status}")
            self.report({'INFO'}, props.status)
            return {'FINISHED'}
        except Exception as e:
            props.status = f"Error: {e}"
            logger.error(f"Operator run_audit failed: {e}", exc_info=True)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

class IFC_OT_refresh_issue_list(bpy.types.Operator):
    bl_idname = "ifc_auditor.refresh_issue_list"
    bl_label = "Refresh list"

    def execute(self, context):
        refresh_issue_list(context)
        return {'FINISHED'}

class IFC_OT_show_issue_category(bpy.types.Operator):
    bl_idname = "ifc_auditor.show_issue_category"
    bl_label = "Show issues"

    category: bpy.props.StringProperty(name="Category", default="orphans")

    def execute(self, context):
        props = context.scene.ifc_auditor_props
        if not props.has_audit_cache:
            self.report({'WARNING'}, "Run the audit first")
            return {'CANCELLED'}
        props.issue_filter = self.category
        refresh_issue_list(context)
        count = len(context.scene.ifc_auditor_issues)
        props.status = f"Showing {count} rows for {self.category}"
        return {'FINISHED'}

class IFC_OT_toggle_group(bpy.types.Operator):
    bl_idname = "ifc_auditor.toggle_group"
    bl_label = "Expand or collapse group"

    index: bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        if self.index < 0 or self.index >= len(scene.ifc_auditor_issues):
            return {'CANCELLED'}
        item = scene.ifc_auditor_issues[self.index]
        item.is_expanded = not item.is_expanded
        return {'FINISHED'}

class IFC_OT_select_active_issue(bpy.types.Operator):
    bl_idname = "ifc_auditor.select_active_issue"
    bl_label = "Go to issue"

    def execute(self, context):
        scene = context.scene
        if not scene.ifc_auditor_issues:
            self.report({'WARNING'}, "No issues in the list")
            return {'CANCELLED'}

        index = min(max(scene.ifc_auditor_issues_index, 0), len(scene.ifc_auditor_issues) - 1)
        item = scene.ifc_auditor_issues[index]
        from .props import UI_FLAT_LIST
        payload = UI_FLAT_LIST[item.payload_index] if 0 <= item.payload_index < len(UI_FLAT_LIST) else {}
        ids = []

        if item.is_group:
            if item.issue_type in {"missing_properties", "heavy_brep"}:
                ids = [e["id"] for e in payload.get("elements", [])]
        else:
            if item.issue_type == "duplicate_guids":
                ids = payload.get("ids", [])
            elif item.ifc_id > 0:
                ids = [item.ifc_id]

        if not ids:
            self.report({'INFO'}, "This issue has no selectable elements")
            return {'CANCELLED'}

        objects = get_objects_from_ifc_ids(ids)
        if not objects:
            self.report({'INFO'}, "No Blender objects found for this issue")
            return {'CANCELLED'}

        selected = select_ifc_ids(ids, focus=True)
        prefs = _get_addon_prefs(context)
        if prefs is not None:
            apply_ghost_highlight(context, objects, item.issue_type, prefs, payload if item.is_group else payload)
        
        status_msg = f"Selected {selected} objects for the active issue"
        context.scene.ifc_auditor_props.status = status_msg
        logger.info(f"Operator select_active_issue: {status_msg}")
        return {'FINISHED'}

class IFC_OT_select_all_listed_issues(bpy.types.Operator):
    bl_idname = "ifc_auditor.select_all_listed_issues"
    bl_label = "Select all listed"

    def execute(self, context):
        ids = []
        from .props import UI_FLAT_LIST
        for item in context.scene.ifc_auditor_issues:
            if item.level > 0:
                continue
            payload = UI_FLAT_LIST[item.payload_index] if 0 <= item.payload_index < len(UI_FLAT_LIST) else {}
            if item.issue_type == "duplicate_guids":
                ids.extend(payload.get("ids", []))
            elif item.issue_type in {"missing_properties", "heavy_brep"} and item.is_group:
                ids.extend(e["id"] for e in payload.get("elements", []))
            elif item.ifc_id > 0:
                ids.append(item.ifc_id)
        ids = sorted(set(int(i) for i in ids if i))
        if not ids:
            self.report({'INFO'}, "No selectable elements in the list")
            return {'CANCELLED'}
        selected = select_ifc_ids(ids, focus=True)
        context.scene.ifc_auditor_props.status = f"Selected {selected} objects from the list"
        return {'FINISHED'}

class IFC_OT_reset_visual(bpy.types.Operator):
    bl_idname = "ifc_auditor.reset_visual"
    bl_label = "Reset visualization"

    def execute(self, context):
        restore_visual()
        context.scene.ifc_auditor_props.status = "Visualization reset"
        return {'FINISHED'}

class IFC_OT_export_report(bpy.types.Operator):
    bl_idname = "ifc_auditor.export_report"
    bl_label = "Export JSON"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename_ext = ".json"

    def execute(self, context):
        props = context.scene.ifc_auditor_props
        if not props.has_audit_cache:
            self.report({'WARNING'}, "Run the audit first")
            return {'CANCELLED'}
        output = self.filepath or bpy.path.abspath("//ifc_audit_report.json")
        from .props import AUDIT_CACHE
        with open(output, "w", encoding="utf-8") as f:
            json.dump(AUDIT_CACHE, f, ensure_ascii=False, indent=2)
        props.status = f"Report exported to {output}"
        logger.info(f"Operator export_report: {props.status}")
        self.report({'INFO'}, props.status)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.path.abspath("//ifc_audit_report.json"), ".json")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class IFC_OT_export_html_report(bpy.types.Operator):
    bl_idname = "ifc_auditor.export_html_report"
    bl_label = "Export HTML Report"
    bl_description = "Generates and opens a visual HTML report"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename_ext = ".html"

    def execute(self, context):
        props = context.scene.ifc_auditor_props
        if not props.has_audit_cache:
            self.report({'WARNING'}, "Run the audit first")
            return {'CANCELLED'}
        
        try:
            from .props import AUDIT_CACHE
            
            output = self.filepath
            if not output:
                self.report({'ERROR'}, "No file path provided")
                return {'CANCELLED'}
            
            # Create reporter and generate
            reporter = HTMLReporter(AUDIT_CACHE)
            reporter.generate(output)
            
            # Open automatically
            webbrowser.open(f"file://{output}")
            
            props.status = f"Report saved and opened: {output}"
            logger.info(f"Operator export_html_report: {props.status}")
            self.report({'INFO'}, props.status)
            return {'FINISHED'}
        except Exception as e:
            props.status = f"Error: {e}"
            logger.error(f"Operator export_html_report failed: {e}", exc_info=True)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

    def invoke(self, context, event):
        props = context.scene.ifc_auditor_props
        from .props import AUDIT_CACHE
        summary = AUDIT_CACHE.get("summary", {})
        model_name = os.path.splitext(summary.get("file", "Model"))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.filepath = bpy.path.ensure_ext(bpy.path.abspath(f"//IFC_Audit_{model_name}_{timestamp}.html"), ".html")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class IFC_OT_export_clean_copy(bpy.types.Operator):
    bl_idname = "ifc_auditor.export_clean_copy"
    bl_label = "Export optimized copy"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename_ext = ".ifc"

    def execute(self, context):
        props = context.scene.ifc_auditor_props
        filepath = None
        if not props.use_active_ifc:
            filepath = bpy.path.abspath(props.filepath).strip()
            if not filepath or not os.path.exists(filepath):
                props.status = "Error: Invalid file path for export"
                logger.error(f"Operator export_clean_copy: {props.status}")
                self.report({'ERROR'}, "Please specify a valid source IFC file path to clean")
                return {'CANCELLED'}

        try:
            auditor = IFCAuditor.from_bonsai_or_file(filepath)
            from .props import AUDIT_CACHE
            if props.has_audit_cache and AUDIT_CACHE:
                auditor.results = AUDIT_CACHE
            else:
                auditor.run()
            stats = auditor.export_clean_copy(
                self.filepath,
                {
                    "empty_psets": props.clean_empty_psets,
                    "unused_types": props.clean_unused_types,
                },
            )
            props.status = f"Optimized copy saved. Removed elements: {stats['removed']}"
            logger.info(f"Operator export_clean_copy: {props.status} to {self.filepath}")
            self.report({'INFO'}, props.status)
            return {'FINISHED'}
        except Exception as e:
            props.status = f"Error: {e}"
            logger.error(f"Operator export_clean_copy failed: {e}", exc_info=True)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.path.abspath("//ifc_optimized.ifc"), ".ifc")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

classes = [
    IFC_OT_run_audit,
    IFC_OT_refresh_issue_list,
    IFC_OT_show_issue_category,
    IFC_OT_toggle_group,
    IFC_OT_select_active_issue,
    IFC_OT_select_all_listed_issues,
    IFC_OT_reset_visual,
    IFC_OT_export_report,
    IFC_OT_export_html_report,
    IFC_OT_export_clean_copy,
]
