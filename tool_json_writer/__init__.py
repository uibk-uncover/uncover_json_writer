
from .tool_json_writer import Detector, BinaryDetector, CategoricalDetector  # noqa: F401
from .tool_json_writer import ToolJSONWriter  # noqa: F401

# package version
import pkg_resources
try:
    __version__ = pkg_resources.get_distribution("tool_json_writer").version
except pkg_resources.DistributionNotFound:
    __version__ = None

__all__ = ['Detector', 'BinaryDetector', 'CategoricalDetector', 'ToolJSONWriter']
