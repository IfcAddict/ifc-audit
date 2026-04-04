from __future__ import annotations
# Based on original logic from IFC_Auditor (https://github.com/AGRDIGITALBUSSINES/IFC_Auditor)
# by AGR Digital Building (https://agrdb.com)
import bpy

_ORIGINAL_MATERIALS: dict[str, list] = {}
_MATERIAL_NAMES = {
    "ghost": "IFC_AUDITOR_GHOST",
    "orphans": "IFC_AUDITOR_ORPHANS",
    "empty_psets": "IFC_AUDITOR_EMPTY_PSETS",
    "unused_types": "IFC_AUDITOR_UNUSED_TYPES",
    "duplicate_guids": "IFC_AUDITOR_DUPLICATE_GUIDS",
    "missing_properties": "IFC_AUDITOR_MISSING_PROPERTIES",
    "heavy_brep_very_high": "IFC_AUDITOR_HEAVY_BREP_VERY_HIGH",
    "heavy_brep_high": "IFC_AUDITOR_HEAVY_BREP_HIGH",
    "heavy_brep_medium": "IFC_AUDITOR_HEAVY_BREP_MEDIUM",
    "heavy_brep_low": "IFC_AUDITOR_HEAVY_BREP_LOW",
    "default": "IFC_AUDITOR_DEFAULT",
}

_COLOR_ATTR_MAP = {
    "orphans": "color_orphans",
    "empty_psets": "color_empty_psets",
    "unused_types": "color_unused_types",
    "duplicate_guids": "color_duplicate_guids",
    "missing_properties": "color_missing_properties",
}

def _ensure_material(name: str, color, alpha: float):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)

    if not mat.use_nodes:
        mat.use_nodes = True

    if hasattr(mat, "blend_method"):
        mat.blend_method = 'BLEND'
    if hasattr(mat, "surface_render_method"):
        try:
            mat.surface_render_method = 'BLENDED'
        except Exception:
            pass
    if hasattr(mat, "shadow_method"):
        try:
            mat.shadow_method = 'NONE'
        except Exception:
            pass
    if hasattr(mat, "use_backface_culling"):
        mat.use_backface_culling = False

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (float(color[0]), float(color[1]), float(color[2]), 1.0)
    if "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = float(alpha)
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat

def _heavy_brep_color(issue_group_name: str, prefs):
    label = issue_group_name or ""
    if "Muy alto" in label:
        return getattr(prefs, "color_brep_very_high", (1.0, 0.15, 0.15)), _MATERIAL_NAMES["heavy_brep_very_high"]
    if "Alto" in label:
        return getattr(prefs, "color_brep_high", (1.0, 0.50, 0.15)), _MATERIAL_NAMES["heavy_brep_high"]
    if "Medio" in label:
        return getattr(prefs, "color_brep_medium", (1.0, 0.90, 0.15)), _MATERIAL_NAMES["heavy_brep_medium"]
    return getattr(prefs, "color_brep_low", (0.80, 0.80, 0.25)), _MATERIAL_NAMES["heavy_brep_low"]

def _highlight_color_for_issue(issue_type: str, prefs, payload: dict | None = None):
    if issue_type == "heavy_brep":
        group_name = ""
        if payload:
            group_name = payload.get("group", "") or payload.get("name", "")
        return _heavy_brep_color(group_name, prefs)

    attr = _COLOR_ATTR_MAP.get(issue_type)
    if attr and hasattr(prefs, attr):
        return getattr(prefs, attr), _MATERIAL_NAMES.get(issue_type, _MATERIAL_NAMES["default"])
    return (1.0, 0.9, 0.2), _MATERIAL_NAMES["default"]

def restore_visual():
    global _ORIGINAL_MATERIALS
    for obj_name, mats in list(_ORIGINAL_MATERIALS.items()):
        obj = bpy.data.objects.get(obj_name)
        if obj is None or getattr(obj, "data", None) is None or not hasattr(obj.data, "materials"):
            continue
        obj.data.materials.clear()
        for mat in mats:
            obj.data.materials.append(mat)
    _ORIGINAL_MATERIALS.clear()

def apply_ghost_highlight(context, active_objects, issue_type: str, prefs, payload: dict | None = None):
    global _ORIGINAL_MATERIALS
    restore_visual()

    active_set = {obj for obj in active_objects if obj is not None}
    if not active_set:
        return 0

    ghost_alpha = max(0.0, min(1.0, 1.0 - float(getattr(prefs, "ghost_alpha", 0.85))))
    ghost_color = getattr(prefs, "ghost_color", (0.8, 0.8, 0.8))
    highlight_color, mat_name = _highlight_color_for_issue(issue_type, prefs, payload)

    ghost_mat = _ensure_material(_MATERIAL_NAMES["ghost"], ghost_color, ghost_alpha)
    highlight_mat = _ensure_material(mat_name, highlight_color, 1.0)

    affected = 0
    for obj in context.view_layer.objects:
        if obj.type != 'MESH' or getattr(obj, "data", None) is None or not hasattr(obj.data, "materials"):
            continue

        _ORIGINAL_MATERIALS[obj.name] = [slot.material for slot in obj.material_slots]
        obj.data.materials.clear()

        if obj in active_set:
            obj.data.materials.append(highlight_mat)
        else:
            obj.data.materials.append(ghost_mat)
        affected += 1
    return affected
