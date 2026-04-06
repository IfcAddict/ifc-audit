import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

try:
    from ifc_audit.core.auditor import IFCAuditor
    from ifc_audit.core.reporter import HTMLReporter
    print("SUCCESS: Core modules imported without bpy!")
except ImportError as e:
    print(f"FAILURE: Could not import core modules: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAILURE: Unexpected error during import: {e}")
    sys.exit(1)

def run_standalone_test():
    # This test assumes a valid IFC file is available or just tests the interface
    # For a real test, we would need a small test.ifc
    print("Initializing Auditor in standalone mode...")
    # Passing a non-existent file just to test initialization doesn't crash on bpy/bonsai
    auditor = IFCAuditor(filepath="non_existent.ifc")
    print("Auditor initialized successfully.")
    
    if auditor.model is None:
        print("Model is None as expected for non-existent file.")
    
    print("\nStandalone Architecture Test PASSED.")

if __name__ == "__main__":
    run_standalone_test()
