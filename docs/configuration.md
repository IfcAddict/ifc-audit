# Configuration Guide - IFC Audit

This guide details how to customize validation rules and visualization in **IFC Audit** according to your project requirements.

---

## 🛠️ Customizing Rules (`core/rules.py`)

The audit logic is based on a central configuration file: `src/ifc_audit/core/rules.py`. You can edit it to:

### 1. Mandatory Properties (`REQUIRED_PROPERTIES`)
Define what properties each type of entity should have. By default:
```python
REQUIRED_PROPERTIES = {
    "IfcWall": ["FireRating", "LoadBearing", "IsExternal"],
    "IfcDoor": ["FireRating", "AcousticRating"],
    "IfcWindow": ["FireRating", "ThermalTransmittance"],
}
```
*   **Add new entity**: Add a line with the name of the IFC class.
*   **Add new property**: Add the exact name of the property to the list.

### 2. Spatial Exclusions (`SPATIAL_ELEMENT_EXCLUSIONS`)
Contains entities that are not analyzed as "orphans" (e.g., Site, Building, Stores).
*   If you want to also ignore **Spaces** (`IfcSpace`), you can add them here.

---

## 👻 Visualization Configuration

You can adjust colors and transparency directly from the **Blender Preferences**:

1.  `Edit > Preferences > Add-ons`.
2.  Search for **"IFC Audit"** and expand the options.
3.  **Ghost Transparency**: Controls how transparent elements without errors become (recommended: 0.1 to 0.2).
4.  **Issue Colors**: Customize the color for each issue type (Orphans, duplicate GUIDs, empty PSets, etc.).

---

## ⚡ Heavy BRep Thresholds

The "Heavy BRep" rule sorts elements by their geometric face count. Current thresholds are:

| Range | Faces | Recommended Color |
| :--- | :--- | :--- |
| **Very High** | > 1000 | Intenso Red |
| **High** | 500 - 1000 | Orange |
| **Medium** | 100 - 500 | Yellow |
| **Low** | < 100 | Lime Green |

> [!IMPORTANT]
> Changing these thresholds requires editing the logic in `core/auditor.py` (function `rule_heavy_brep`). In future versions, this will be configurable from the UI.
