"""
Custom tools for mock image pipeline
"""

import os
import sys
import time
import shutil

# =====================================================================

def copy_ebs_file(src, dst, max_retries=3):
    """
    Copy an Amazon EBS file with retries after temporary failure.
    """

    delay = 2
    for attempt in range(max_retries):
        try:
            shutil.copy2(src, dst)
            return
        except (IOError, OSError) as e:
            print(f"Copy EBS file attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = delay ** attempt
                time.sleep(2**attempt) # Wait before retrying
            else:
                print(f"All {max_retries} copy EBS file attempts failed")
                raise # Re-raise exception if all retries fail

# ----------------------------------------------------------------------------

def remove_ebs_file(filepath, max_attempts=3):
    """
    Remove an Amazon EBS file with retries after temporary failure.
    """

    attempt = 1
    delay   = 2

    while attempt <= max_attempts:
        try:
            os.remove(filepath)
            return
        except (OSError, FileNotFoundError) as e:
            # Handle EBS temporary glitches (e.g., EIO - 5, ETIMEDOUT - 110)
            if isinstance(e, FileNotFoundError) or e.errno in [5, 110]:
                wait_time = delay ** (attempt - 1)
                print(f"EBS temporary error {e} with error #{e.errno}, attempt #{attempt}, retrying in {wait_time}s...")
                time.sleep(wait_time)
                attempt += 1
            else:
                raise e # Re-raise if it's a permanent error (e.g., PermissionError)

    raise Exception(f"Failed to remove {filepath} after {max_attempts} attempts")

# --------------------------------------------------------------------------------

if __name__ == "__main__":
    print("Error: This file cannot be run directly. Please import it as a module.")
    sys.exit(1)

