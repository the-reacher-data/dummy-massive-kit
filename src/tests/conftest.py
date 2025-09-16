"""Test configuration for dummy_massivekit."""
import sys
from pathlib import Path

# Add src directory to Python path so tests can import modules without installation
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))
