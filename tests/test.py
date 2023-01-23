
import sys
import unittest
sys.path.append(".")

# logging
if __name__ == "__main__":
    import logging
    logging.basicConfig(filename="test.log", level=logging.INFO)
    import tool_json_writer
    logging.info(f"{tool_json_writer.__path__=}")

# === unit tests ===
from test_writer import TestWriter  # noqa: F401,E402
# ==================

# run unittests
if __name__ == "__main__":
    unittest.main(verbosity=1)