# User Guide - IFC Audit

This guide explains how to use the validation tools in **IFC Audit** within Blender + Bonsai to ensure the quality of your BIM models.

---

## 🚀 Recommended Workflow

For best results, follow this order:

1.  **Load the Model**: Ensure you have an active IFC model in **Bonsai** (BlenderBIM) or specify a local file path.
    - *Tip:* You can also run the audit without Blender using the CLI script.
2.  **Initial Analysis**: Click the **"Run Audit"** button in the sidebar (N-key > `IFC` tab).
3.  **Visual Inspection**: Navigate through the issue tree. Use **Ghost Mode** to isolate problems.
4.  **Direct Cleanup**: Execute cleanup actions (like removing empty PSets) if the model allows.
5.  **Export**: Generate a detailed HTML report, a JSON report, or an optimized IFC copy to share with the team.

---

## 🔍 Audit Rules Explained

### 1. Orphans
Detects products that are not assigned to any Building Storey.
- **Error**: The element has no spatial relación or assignment.
- **Warning**: The element has no spatial container but has other relations (like systems or groups).

### 2. Empty Property Sets
Identifies property set containers (`IfcPropertySet`) that do not contain any real properties. These elements inflate the file size without contributing information.

### 3. Unused Types
Often, exporters include type definitions (`IfcTypeObject`) that are not used in the actual model. Identifying them helps clean the project's type "dictionary."

### 4. Duplicate GUIDs
A critical integrity rule. Two elements should not have the same Global Identifier. If they do, it can cause serious issues in viewers and databases.

### 5. Missing Properties
Checks if key elements (Walls, Doors, Windows) have the mandatory technical properties defined in the project configuration (e.g., *FireRating*).

### 6. Heavy BRep
Analyzes geometric complexity by checking the face count of boundary representations (BReps). Visualizes elements as green, yellow, orange, or red based on weight.

---

## 👻 Ghost Mode and Visualization
To make the audit intuitive, **IFC Audit** uses temporary materials:

- **Ghost Mode**: Parts of the model without errors become translucent.
- **Issue Highlighting**: Each type of error is assigned a color (red, orange, yellow) to identify the problem at a glance without permanently modifying your file's materials.

> [!TIP]
> You can adjust the ghost mode transparency in the **Add-on Preferences**.

---

## 📁 Exporting Results

- **HTML Report**: Automatically generates a professional report dashboard and saves it directly to your `Downloads/` folder, popping up in your default web browser instantly. It summarizes issues, shows entity inventory, and features detailed tables.
- **Optimized IFC Copy**: Generates a new file automatically removing what you don't need (empty PSets, unused types).
- **JSON Report**: Ideal for integrating with other data workflows or quality dashboards.
