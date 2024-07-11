# tests/conftest.py
import sys
import os

#die fiel ist zum konfigurieren für die unit tests, die mit "test_production_operations.py" durchgeführt werden

# Get the absolute path of the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


