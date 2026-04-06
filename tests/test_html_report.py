from src.ifc_audit.core.reporter import HTMLReporter
import os
import json

def test_html_report():
    # Mock data
    results = {
        "summary": {
            "file": "Test_Model.ifc",
            "file_size_mb": 12.5,
            "total_entities": 1500,
            "total_issues": 3,
            "schema": "IFC4"
        },
        "inventory": {
            "IfcWall": 100,
            "IfcWindow": 50,
            "IfcDoor": 20
        },
        "issues": {
            "orphans": [
                {"id": 101, "name": "Wall_01", "type": "IfcWall", "severity": "error"},
                {"id": 102, "name": "Window_02", "type": "IfcWindow", "severity": "warning"}
            ],
            "duplicate_guids": [
                {"guid": "ABC-123", "count": 2, "ids": [201, 202]}
            ],
            "heavy_brep": [
                {
                    "group": "Very High (>1000)",
                    "elements": [{"id": 301, "name": "Complex_Mesh", "type": "IfcFacetedBrep", "faces": 5000}]
                }
            ]
        }
    }
    
    reporter = HTMLReporter(results)
    output_path = "test_audit_report.html"
    reporter.generate(output_path)
    
    if os.path.exists(output_path):
        print(f"SUCCESS: HTML report generated at {os.path.abspath(output_path)}")
        # Check for keywords in the file
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "IFC Audit Report" in content and "Test INFO message" not in content:
                print("HTML content seems valid.")
            else:
                print("HTML content verification FAILED.")
    else:
        print("FAILURE: HTML report was not generated.")

if __name__ == "__main__":
    test_html_report()
