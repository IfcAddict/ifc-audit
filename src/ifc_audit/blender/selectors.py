from __future__ import annotations
import bpy

def get_bonsai_tool():
    try:
        import bonsai.tool as tool  # type: ignore
        return tool
    except Exception:
        return None

def get_model():
    tool = get_bonsai_tool()
    if tool is None:
        return None
    try:
        return tool.Ifc.get()
    except Exception:
        return None

def get_file_path():
    tool = get_bonsai_tool()
    if tool is None:
        return None
    try:
        # Bonsai/BlenderBIM usually provides a tool to get the active project path
        return tool.Ifc.get_path()
    except Exception:
        return None

def clear_selection():
    try:
        bpy.ops.object.select_all(action='DESELECT')
    except Exception:
        pass

def focus_active_view3d():
    window = bpy.context.window
    if window is None:
        return False
    screen = window.screen
    if screen is None:
        return False
    for area in screen.areas:
        if area.type != 'VIEW_3D':
            continue
        region = next((r for r in area.regions if r.type == 'WINDOW'), None)
        if region is None:
            continue
        with bpy.context.temp_override(window=window, area=area, region=region):
            try:
                bpy.ops.view3d.view_selected(use_all_regions=False)
                return True
            except Exception:
                continue
    return False

def get_objects_from_ifc_ids(ifc_ids):
    tool = get_bonsai_tool()
    model = get_model()
    if tool is None or model is None:
        return []

    objects = []
    seen = set()
    for ifc_id in ifc_ids:
        try:
            ent = model.by_id(int(ifc_id))
            if ent is None:
                continue
            obj = tool.Ifc.get_object(ent)
            if obj is None:
                continue
            key = getattr(obj, "name", None) or id(obj)
            if key in seen:
                continue
            seen.add(key)
            objects.append(obj)
        except Exception:
            continue
    return objects

def select_ifc_ids(ifc_ids, focus=False):
    clear_selection()
    objects = get_objects_from_ifc_ids(ifc_ids)
    active_obj = None
    selected = 0

    for obj in objects:
        try:
            obj.select_set(True)
            if active_obj is None:
                active_obj = obj
            selected += 1
        except Exception:
            continue

    if active_obj is not None:
        try:
            bpy.context.view_layer.objects.active = active_obj
        except Exception:
            pass
        if focus:
            focus_active_view3d()
    return selected
