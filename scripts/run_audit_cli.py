import sys
import os
from datetime import datetime

# 1. Add 'src' to the Python path
# This allows importing 'ifc_audit' as a package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

try:
    from ifc_audit.core.auditor import IFCAuditor
    from ifc_audit.core.reporter import HTMLReporter
except ImportError as e:
    print(f"Error: Could not import ifc_audit core modules: {e}")
    print("Ensure you are in the project root and have ifcopenshell installed.")
    sys.exit(1)

def run_standalone_audit(ifc_path):
    """
    Executes a complete IFC audit without Blender or Bonsai.
    Generates a professional HTML report in the user's Downloads folder.
    """
    if not os.path.exists(ifc_path):
        print(f"Error: File not found: {ifc_path}")
        return

    print(f"\n[IFC Audit] Starting standalone audit for: {os.path.basename(ifc_path)}")
    print("-" * 50)

    try:
        # Initialize auditor (auto-detects standalone mode because no Blender environment is present)
        auditor = IFCAuditor(filepath=ifc_path)
        
        # Run everything
        print("Progress: Analyzing geometry and BIM data...")
        results = auditor.run()
        
        # Determine output path (Downloads folder)
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(downloads_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_base = os.path.splitext(os.path.basename(ifc_path))[0]
        report_filename = f"Standalone_Audit_{model_base}_{timestamp}.html"
        report_path = os.path.join(downloads_dir, report_filename)
        
        print(f"Progress: Found {results['summary']['total_issues']} issues.")
        print("Progress: Generating HTML report...")
        
        reporter = HTMLReporter(results)
        reporter.generate(report_path)
        
        print("-" * 50)
        print(f"SUCCESS: Audit report generated successfully!")
        print(f"Location: {report_path}")
        print("-" * 50)
        
    except Exception as e:
        print(f"FATAL ERROR during audit: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/run_audit_cli.py <path_to_your_file.ifc>")
    else:
        run_standalone_audit(sys.argv[1])
