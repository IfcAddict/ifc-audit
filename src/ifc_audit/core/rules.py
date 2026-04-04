from __future__ import annotations

REQUIRED_PROPERTIES = {
    "IfcWall": ["FireRating", "LoadBearing", "IsExternal"],
    "IfcDoor": ["FireRating", "AcousticRating"],
    "IfcWindow": ["FireRating", "ThermalTransmittance"],
}

SPATIAL_ELEMENT_EXCLUSIONS = {
    "IfcProject",
    "IfcSite",
    "IfcBuilding",
    "IfcBuildingStorey",
    "IfcSpace",
}

DEFAULT_CLEAN_OPTIONS = {
    "empty_psets": True,
    "unused_types": True,
}

ISSUE_TITLES = {
    "orphans": "Orphans",
    "empty_psets": "Empty PSets",
    "unused_types": "Unused Types",
    "duplicate_guids": "Duplicate GUIDs",
    "missing_properties": "Missing Properties",
}

ISSUE_TITLES["heavy_brep"] = "Heavy BRep"
