# IFC Audit

![Blender](https://img.shields.io/badge/Blender-4.x%20%7C%205.x-orange)
![IFC](https://img.shields.io/badge/IFC-OpenBIM-blue)
![Status](https://img.shields.io/badge/status-active-success)
![License](https://img.shields.io/badge/license-GPLv3-lightgrey)

Blender + Bonsai addon for **analyzing, validating, and improving the quality of IFC models** from a structural, semantic, and geometric perspective.

---

## 📖 Documentation

- [User Guide](docs/user_guide.md): How to use audit rules and Ghost Mode.
- [Configuration Guide](docs/configuration.md): Customizing rules and colors.
- [Developer Guide](docs/development.md): Architecture and how to contribute.

---

## What is this?

IFC Audit is not a viewer. It is a tool to:

- Understand the real quality of an IFC.
- Detect structural issues.
- Analyze information (not just geometry).
- Operate directly on the model.

👉 **Move from "viewing models" to "analyzing data".**

---

## Overview

### Issue Navigation (Tree UI)
![UI Tree](docs/images/ui_tree.png)
- Grouping by error type.
- Hierarchical navigation.
- Direct selection in viewport.

### Highlight + Ghost Mode
![Highlight](docs/images/highlight.gif)
- Non-destructive visual isolation.
- Colors mapped to issue types.
- Automatic focus in the viewport.

### Heavy BRep Analysis
![Brep](docs/images/brep.png)
- Detection of complex geometry.
- Sorting by face count.
- Grouping by performance impact.

---

## Features

### IFC Analysis
- Reading from active Bonsai model or local file.
- Entity inventory and global summary.

### Structural Validation
- Orphan element detection.
- Severity classification (Error/Warning).
- Exclusion of `IfcVirtualElement`.

### Model Consistency
- Empty property sets.
- Unused IFC types.
- Duplicate GUIDs.

### Semantic Validation
- Checking for mandatory properties.
- Grouping by missing property type.

### Geometric Quality
- Detection of `IfcFacetedBrep` and `IfcAdvancedBrep`.
- Complexity calculation based on face count.

---

## Installation

### Requirements
- Blender 4.x or 5.x.
- Bonsai installed.

### Steps
1. Download the repository as a `.zip`.
2. In Blender: `Edit > Preferences > Add-ons > Install...`.
3. Select the downloaded file and enable: **IFC Audit**.

---

## Credits, References and License

This project is an evolution and adaptation for Blender/Bonsai of the original work by **AGR Digital Building**.
Due to its integration with the Blender Python API, this project is distributed under the **GNU GPLv3** license.

**Original Base Logic Acknowledgment:**
Portions of the core logic in this software are based on the original work by AGR Digital Building, which is licensed under the MIT License. You can find the original base logic here:
- **Original Base Code:** [IFC_Auditor](https://github.com/AGRDIGITALBUSSINES/IFC_Auditor)
- **Original Author:** Andrés G. Rodríguez (AGR Digital Building, https://agrdb.com).

Thanks to AGR Digital Building for their fantastic contribution to the open BIM community and for laying the logical foundation of this audit tool.
