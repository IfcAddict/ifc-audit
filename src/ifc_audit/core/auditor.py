from __future__ import annotations
# Based on original logic from IFC_Auditor (https://github.com/AGRDIGITALBUSSINES/IFC_Auditor)
# by AGR Digital Building (https://agrdb.com)

import os
from collections import Counter, defaultdict
from datetime import datetime

import ifcopenshell
import ifcopenshell.util.element as util_element

from .rules import REQUIRED_PROPERTIES, SPATIAL_ELEMENT_EXCLUSIONS
from .logger import get_logger

logger = get_logger()

class IFCAuditor:
    def __init__(self, model=None, filepath: str | None = None):
        self.model = model
        self.filepath = filepath
        self.file_size_mb = None
        
        # If no model is provided, try to load it from filepath
        if not self.model and self.filepath and os.path.exists(self.filepath):
            try:
                self.model = ifcopenshell.open(self.filepath)
            except Exception as e:
                logger.error(f"Could not load IFC from {self.filepath}: {e}")

        # If still no model, only then try to use the Blender environment if available
        if not self.model:
            self._try_load_from_blender()

        self._set_filesize_if_possible()
        self.results = {
            "summary": {},
            "inventory": {},
            "issues": {
                "empty_psets": [],
                "orphans": [],
                "unused_types": [],
                "duplicate_guids": [],
                "missing_properties": [],
                "heavy_brep": [],
                "geometry": {},
            },
            "metadata": {},
        }
        self._set_filesize_if_possible()

    @classmethod
    def from_bonsai_or_file(cls, filepath: str | None = None):
        model = get_model()
        if model is not None:
            return cls(model=model, filepath=filepath)
        if filepath and os.path.exists(filepath):
            model = ifcopenshell.open(filepath)
            logger.info(f"Loaded IFC model from file: {filepath}")
            return cls(model=model, filepath=filepath)
        
        msg = "No active IFC model in Bonsai and no valid IFC path provided."
        logger.error(msg)
        raise RuntimeError(msg)

    def _try_load_from_blender(self):
        try:
            # Lazy import to avoid bpy/bonsai dependencies in standalone mode
            from ..blender.selectors import get_model, get_file_path
            self.model = get_model()
            if not self.filepath:
                self.filepath = get_file_path()
            if self.model:
                logger.info("Retrieved active IFC model from Blender/Bonsai")
        except ImportError:
            # Not running inside Blender or module not found
            pass
        except Exception as e:
            logger.debug(f"Failed to auto-load from Blender: {e}")

    def _set_filesize_if_possible(self):
        if self.filepath and os.path.exists(self.filepath):
            self.file_size_mb = round(os.path.getsize(self.filepath) / (1024 * 1024), 2)

    def analyze_inventory(self):
        logger.info("Analyzing model inventory (geometric only)...")
        # Only consider IfcProducts that have a defined Representation
        geometric_entities = [
            e.is_a() for e in self.model.by_type("IfcProduct")
            if getattr(e, "Representation", None) is not None
        ]
        counts = Counter(geometric_entities)
        self.results["inventory"] = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
        return self.results["inventory"]

    def rule_empty_psets(self):
        logger.info("Running rule: Empty Property Sets...")
        empty = []
        total = 0
        duplicate_names = Counter()
        for pset in self.model.by_type("IfcPropertySet"):
            total += 1
            name = getattr(pset, "Name", None)
            if name:
                duplicate_names[name] += 1
            if not getattr(pset, "HasProperties", None):
                empty.append({
                    "id": pset.id(),
                    "name": name or f"PSet_{pset.id()}",
                    "type": pset.is_a(),
                })
        self.results["issues"]["empty_psets"] = empty
        self.results["metadata"]["total_psets"] = total
        self.results["metadata"]["duplicate_pset_names"] = {k: v for k, v in duplicate_names.items() if v > 1}
        return empty

    def rule_orphans(self):
        logger.info("Running rule: Orphans...")
        grouped = {}
        for product in self.model.by_type("IfcProduct"):
            if product.is_a() in SPATIAL_ELEMENT_EXCLUSIONS:
                continue
            if product.is_a("IfcVirtualElement"):
                continue

            try:
                container = util_element.get_container(product)
            except Exception:
                container = None

            if not container:
                has_rel = (
                    getattr(product, "IsDefinedBy", None)
                    or getattr(product, "HasAssignments", None)
                    or getattr(product, "ConnectedTo", None)
                )

                severity = "warning" if has_rel else "error"
                ifc_type = product.is_a()
                
                if ifc_type not in grouped:
                    grouped[ifc_type] = {
                        "type": ifc_type,
                        "elements": []
                    }

                grouped[ifc_type]["elements"].append({
                    "id": product.id(),
                    "type": ifc_type,
                    "name": getattr(product, "Name", None) or f"Elem_{product.id()}",
                    "severity": severity,
                })

        result = list(grouped.values())
        result.sort(key=lambda x: len(x["elements"]), reverse=True)
        self.results["issues"]["orphans"] = result
        return result

    def rule_unused_types(self):
        logger.info("Running rule: Unused Types...")
        unused = []
        for ifc_type in self.model.by_type("IfcTypeObject"):
            used = False

            try:
                if hasattr(ifc_type, "Types") and ifc_type.Types:
                    for rel in ifc_type.Types:
                        if rel and hasattr(rel, "RelatedObjects") and rel.RelatedObjects:
                            used = True
                            break
            except Exception:
                pass

            try:
                if not used and hasattr(ifc_type, "ObjectTypeOf") and ifc_type.ObjectTypeOf:
                    for rel in ifc_type.ObjectTypeOf:
                        if rel and hasattr(rel, "RelatedObjects") and rel.RelatedObjects:
                            used = True
                            break
            except Exception:
                pass

            if not used:
                unused.append({
                    "id": ifc_type.id(),
                    "type": ifc_type.is_a(),
                    "name": getattr(ifc_type, "Name", None) or f"Type_{ifc_type.id()}",
                })
        self.results["issues"]["unused_types"] = unused
        return unused

    def rule_duplicate_guids(self):
        logger.info("Running rule: Duplicate GUIDs...")
        guid_map = defaultdict(list)
        for entity in self.model:
            guid = getattr(entity, "GlobalId", None)
            if guid:
                guid_map[guid].append(entity)

        duplicates = []
        for guid, entities in guid_map.items():
            if len(entities) > 1:
                duplicates.append({
                    "guid": guid,
                    "count": len(entities),
                    "ids": [e.id() for e in entities],
                    "name": f"{guid} ({len(entities)})",
                    "type": "DuplicateGUID",
                })

        duplicates.sort(key=lambda x: x["count"], reverse=True)
        self.results["issues"]["duplicate_guids"] = duplicates
        return duplicates

    def rule_missing_properties(self):
        logger.info("Running rule: Missing Properties...")
        grouped = {}

        def has_property(element, prop_name):
            if not hasattr(element, "IsDefinedBy"):
                return False
            for rel in element.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByProperties"):
                    pset = rel.RelatingPropertyDefinition
                    if pset.is_a("IfcPropertySet"):
                        for prop in pset.HasProperties:
                            if prop.Name == prop_name:
                                return True
            return False

        for ifc_type, props in REQUIRED_PROPERTIES.items():
            for elem in self.model.by_type(ifc_type):
                missing = [p for p in props if not has_property(elem, p)]
                for prop in missing:
                    if prop not in grouped:
                        grouped[prop] = {
                            "property": prop,
                            "elements": []
                        }
                    grouped[prop]["elements"].append({
                        "id": elem.id(),
                        "name": getattr(elem, "Name", None) or f"Elem_{elem.id()}",
                        "type": elem.is_a()
                    })

        result = list(grouped.values())
        result.sort(key=lambda x: len(x["elements"]), reverse=True)
        self.results["issues"]["missing_properties"] = result
        return result

    def _count_brep_faces(self, item):
        count = 0
        try:
            if item.is_a("IfcFacetedBrep"):
                shell = getattr(item, "Outer", None)
                if shell and hasattr(shell, "CfsFaces"):
                    count += len(shell.CfsFaces)
            elif item.is_a("IfcAdvancedBrep"):
                shell = getattr(item, "Outer", None)
                if shell and hasattr(shell, "Faces"):
                    count += len(shell.Faces)
        except Exception:
            pass
        return count

    def rule_heavy_brep(self):
        logger.info("Running rule: Heavy BRep...")
        elements = []

        for elem in self.model.by_type("IfcProduct"):
            representation = getattr(elem, "Representation", None)
            if not representation or not getattr(representation, "Representations", None):
                continue

            total_faces = 0
            is_brep = False

            for rep in representation.Representations:
                for item in getattr(rep, "Items", []) or []:
                    try:
                        if item.is_a("IfcFacetedBrep") or item.is_a("IfcAdvancedBrep"):
                            is_brep = True
                            total_faces += self._count_brep_faces(item)
                    except Exception:
                        continue

            if is_brep and total_faces > 0:
                elements.append({
                    "id": elem.id(),
                    "name": getattr(elem, "Name", None) or f"Elem_{elem.id()}",
                    "type": elem.is_a(),
                    "faces": total_faces,
                })

        elements.sort(key=lambda x: x["faces"], reverse=True)

        groups = {
            "Very High (>1000)": [],
            "High (500-1000)": [],
            "Medium (100-500)": [],
            "Low (<100)": [],
        }

        for e in elements:
            f = e["faces"]
            if f > 1000:
                groups["Very High (>1000)"].append(e)
            elif f > 500:
                groups["High (500-1000)"].append(e)
            elif f > 100:
                groups["Medium (100-500)"].append(e)
            else:
                groups["Low (<100)"].append(e)

        result = [{"group": k, "elements": v} for k, v in groups.items() if v]
        self.results["issues"]["heavy_brep"] = result
        return result

    def rule_geometry(self):
        rep_types = Counter()
        for rep in self.model.by_type("IfcShapeRepresentation"):
            rep_type = getattr(rep, "RepresentationType", None)
            if rep_type:
                rep_types[rep_type] += 1
        self.results["issues"]["geometry"] = dict(rep_types)
        return self.results["issues"]["geometry"]

    def build_summary(self):
        total_entities = sum(self.results["inventory"].values())
        issues = self.results["issues"]
        total_issues = (
            sum(len(g.get("elements", [])) for g in issues["orphans"]) +
            len(issues["empty_psets"]) +
            len(issues["unused_types"]) +
            len(issues["duplicate_guids"]) +
            len(issues["missing_properties"]) +
            sum(len(g.get("elements", [])) for g in issues["heavy_brep"])
        )
        self.results["summary"] = {
            "schema": getattr(self.model, "schema", "Unknown"),
            "file": os.path.basename(self.filepath) if self.filepath else "Active IFC in Bonsai",
            "file_size_mb": self.file_size_mb,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_entities": total_entities,
            "total_issues": total_issues,
            "empty_psets": len(issues["empty_psets"]),
            "orphans": sum(len(g.get("elements", [])) for g in issues["orphans"]),
            "unused_types": len(issues["unused_types"]),
            "duplicate_guids": len(issues["duplicate_guids"]),
            "missing_properties": len(issues["missing_properties"]),
            "heavy_brep": sum(len(g.get("elements", [])) for g in issues["heavy_brep"]),
        }
        return self.results["summary"]

    def run(self):
        logger.info("Starting full audit process...")
        self.analyze_inventory()
        self.rule_empty_psets()
        self.rule_orphans()
        self.rule_unused_types()
        self.rule_duplicate_guids()
        self.rule_missing_properties()
        self.rule_heavy_brep()
        self.rule_geometry()
        self.build_summary()
        logger.info(f"Audit complete. Total issues found: {self.results['summary']['total_issues']}")
        return self.results

    def get_issue_ids(self, category: str):
        issues = self.results.get("issues", {}).get(category, [])
        ids = []
        if category == "orphans":
            for item in issues:
                ids.extend(e["id"] for e in item.get("elements", []))
            return ids
        if category == "duplicate_guids":
            for item in issues:
                ids.extend(item.get("ids", []))
            return ids
        if category == "missing_properties":
            for item in issues:
                ids.extend(e["id"] for e in item.get("elements", []))
            return ids
        if category == "heavy_brep":
            for item in issues:
                ids.extend(e["id"] for e in item.get("elements", []))
            return ids
        for item in issues:
            if isinstance(item, dict) and "id" in item:
                ids.append(item["id"])
        return ids

    def clean(self, options: dict):
        removed = 0
        if options.get("empty_psets"):
            for pset in self.results.get("issues", {}).get("empty_psets", []):
                ent = self.model.by_id(pset["id"])
                if ent:
                    try:
                        self.model.remove(ent)
                        removed += 1
                    except Exception:
                        pass
        if options.get("unused_types"):
            for type_item in self.results.get("issues", {}).get("unused_types", []):
                ent = self.model.by_id(type_item["id"])
                if ent:
                    try:
                        self.model.remove(ent)
                        removed += 1
                    except Exception:
                        pass
        return removed

    def export_clean_copy(self, output_path: str, options: dict):
        removed = self.clean(options)
        self.model.write(output_path)
        size_mb = round(os.path.getsize(output_path) / (1024 * 1024), 2) if os.path.exists(output_path) else None
        return {
            "removed": removed,
            "output_path": output_path,
            "output_size_mb": size_mb,
        }
