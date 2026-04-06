# Developer Guide - IFC Audit

This guide is for anyone interested in contributing to the development of **IFC Audit** or understanding its technical architecture.

---

## 🏗️ Technical Architecture

The code follows a decoupled pattern to separate BIM analysis logic from the Blender interface:

### 1. Central Engine (`src/ifc_audit/core/`)
Fully independent from the UI. It uses **IfcOpenShell** to operate on IFC data.
*   **`auditor.py`**: Contains the `IFCAuditor` class. Each rule is an independent method that returns a result dictionary compatible with JSON files.
*   **`highlight.py`**: Translates the issues into Blender materials (`bpy.data.materials`) in a non-destructive way.
*   **`reporter.py`**: Generates standalone HTML dashboards and reports out of the audit data.
*   **`logger.py`**: Centralized dual-logging interface for Blender Console and persistent log files.

### 2. Blender Integration (`src/ifc_audit/blender/`)
Components that strictly depend on the Blender API (`bpy`).
*   **`panel.py`**: Builds the dynamic tree interface to navigate errors.
*   **`operators.py`**: Bridge that connects user interactions in the panel with the logic in `core`.
*   **`props.py`**: Defines the add-on's persistent data (`RNA properties`) for UI state.
*   **`selectors.py`**: Responsible for identifying the active IFC model from the **Bonsai** environment context.

---

## 🏗️ How to Add a New Audit Rule

### Step 1: Define the logic in `core/auditor.py`
Add a new method to the `IFCAuditor` class (e.g., `rule_my_custom_check`). It should save the results in `self.results["issues"]["my_custom_check"]`.

### Step 2: Register the title in `core/rules.py`
To correctly show the name in the UI, add an entry to the `ISSUE_TITLES` dictionary.

### Step 3: Activate the rule in the `run()` method
Ensure your new method is called within the `run()` function in `auditor.py`.

---

## 📦 Dependencies

This add-on depends on:
- **Blender 4.x / 5.x**
- **IfcOpenShell**: Usually included with the Bonsai installation.

For external development of the `core` logic, you can install IfcOpenShell via pip:
```bash
pip install ifcopenshell
```

---

## 🧪 Testing and CLI

It's recommended to use small synthetic IFC files (located in `tests/data/`) to validate new audit rules before testing them on large production models.

Because the core logic is physically decoupled from `bpy`, you can test auditing on raw IFC files entirely outside of Blender by using the dedicated Python script:
```bash
python scripts/run_audit_cli.py tests/My_Model.ifc
```

---

## 🚀 CI/CD Automation

This repository uses **GitHub Actions** (`.github/workflows/build_and_release.yml`) to govern the delivery lifecycle:
- On every push, changes are tested using `scripts/run_audit_cli.py`.
- On pushing a new version tag (e.g., `v0.2.1`), the pipeline automatically builds `ifc_audit_v0.2.1.zip` and sets up a new GitHub Release with the corresponding release notes fetched from `CHANGELOG.md`.
