from src.ifc_audit.core.logger import setup_logger, get_logger
import os

def test_logging():
    # Setup
    logger = setup_logger(log_to_file=True)
    
    # Log some messages
    logger.info("Test INFO message")
    logger.debug("Test DEBUG message")
    logger.error("Test ERROR message")
    
    # Check if directory exists
    log_dir = os.path.join(os.path.expanduser("~"), ".ifc_audit")
    log_path = os.path.join(log_dir, "ifc_audit.log")
    
    if os.path.exists(log_path):
        print(f"SUCCESS: Log file found at {log_path}")
        with open(log_path, 'r') as f:
            content = f.read()
            print("Log Content Snapshot:")
            print(content[-200:])
    else:
        print(f"FAILURE: Log file NOT found at {log_path}")

if __name__ == "__main__":
    test_logging()
