from pathlib import Path
import runpy
import sys

project_root = Path(__file__).parent / "uac-care-load-analytics"
sys.path.insert(0, str(project_root))
runpy.run_path(str(project_root / "app.py"), run_name="__main__")
