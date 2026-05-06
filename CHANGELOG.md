# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2026-05-06

### Fixed
- **Data Integrity:** `clean` operation now safely removes inverse relationships (`IfcRelDefinesByProperties`, `IfcRelDefinesByType`) before deleting entities to prevent IFC corruption.
- **Security (XSS):** Dynamically generated HTML reports now escape all IFC string values using `html.escape()`.
- **UI Lag & Performance:** Replaced the use of Blender's `StringProperty` for storing huge JSON strings with global Python state, eliminating lag on large models.
- **Ghost Mode Bugs:** Fixed a bug where non-IFC MESH objects in the scene were incorrectly affected by Ghost Mode. Materials are now tracked by internal object pointers instead of string names to survive renaming. Ghost materials are cleanly purged upon restoring visualization.

### Changed
- **HTML Export Path:** HTML report generation now uses Blender's native file browser, allowing the user to pick the export directory instead of forcing it to `Downloads/`.
- **Performance:** Dramatically optimized `rule_missing_properties` to `O(N)` via sets, speeding up audits on massive files.

## [0.2.1] - 2026-04-06

### Fixed
- **UI Version:** Added standard version mapping and updated.
- **Standalone Logic:** Fixed legacy `get_model` reference for hybrid loading (`from_bonsai_or_file`).
- **HTML Export Bug:** Fixed `datetime` missing import error when exporting HTML from Blender.

### Added
- **Detailed HTML Reports:** Expanded HTML reporter to render missing property counts, empty psets, and unused types tables.

## [0.2.0] - 2026-04-06

### Added
- **Professional Reporting Engine:** Generates standalone HTML reports with modern CSS, dashboard summaries, and detailed issue tables.
- **Automatic Export Workflow:** Reports are now saved automatically to the `Downloads/` folder and opened in the default browser.
- **Architectural Decoupling:** The core audit engine is now independent of Bonsai/Blender, allowing for standalone CLI usage and batch processing.
- **CI/CD Automation:** GitHub Actions workflow for automated ZIP packaging, logic validation, and synchronized releases.
- **Smart Orphan Grouping:** Orphaned elements are now grouped by IFC entity type in both the UI and HTML report for better readability.
- **Customized BRep Severity:** Visual color coding for geometric complexity (Red/Amber/Black/Green) in viewport and reports.
- **Advanced Logging:** Centralized logging system with dual output (Blender Console + persistent log file).

### Changed
- **Memory vs. File Toggle:** Added a checkbox to switch between auditing the active model in memory or an external IFC file.
- **Geometric Inventory:** The model inventory now specifically filters for entities with geometric representations.
- **UI Hierarchy:** Updated the issues tree to support new grouped structures (Orphans, BRep ranges).

## [0.1.0] - 2026-04-04

### Added
- Initial public release of **IFC Audit**.
- Integrated engine for IFC quality and structural validation.
- New tree-based UI for hierarchical issue navigation.
- Non-destructive "Ghost Mode" and highlighting system.
- Support for Blender 4.x and 5.x.
- Automated cleaning for unused types and empty property sets.
- Geometric complexity analysis (BRep face count grouping).
- Optimized IFC export with cleaning options.
- Professional project structure with `src/` layout.

---
Original base logic provided by [AGR Digital Building](https://github.com/AGRDIGITALBUSSINES/IFC_Auditor).
