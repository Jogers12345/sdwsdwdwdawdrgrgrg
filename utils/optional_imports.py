"""
Optional imports wrapper for production deployment
Handles missing dependencies gracefully
"""

import warnings
from typing import Any, Optional

def safe_import_numpy() -> Any:
    """Safely import numpy with fallback"""
    try:
        import numpy
        return numpy
    except ImportError:
        warnings.warn("NumPy not available. Some advanced features will be disabled.", ImportWarning)
        return None

def safe_import_scipy() -> Any:
    """Safely import scipy with fallback"""
    try:
        import scipy
        return scipy
    except ImportError:
        warnings.warn("SciPy not available. Some advanced features will be disabled.", ImportWarning)
        return None

def safe_import_torch() -> Any:
    """Safely import torch with fallback"""
    try:
        import torch
        return torch
    except ImportError:
        warnings.warn("PyTorch not available. Neural network features will be disabled.", ImportWarning)
        return None

def safe_import_tensorflow() -> Any:
    """Safely import tensorflow with fallback"""
    try:
        import tensorflow
        return tensorflow
    except ImportError:
        warnings.warn("TensorFlow not available. Some ML features will be disabled.", ImportWarning)
        return None

# Lazy loading singleton
class ImportManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __getattr__(self, name: str) -> Any:
        if not self._initialized:
            self._initialize_imports()
            self._initialized = True

        return getattr(self, f"_{name}", None)

    def _initialize_imports(self):
        """Initialize all optional imports"""
        self._numpy = safe_import_numpy()
        self._scipy = safe_import_scipy()
        self._torch = safe_import_torch()
        self._tensorflow = safe_import_tensorflow()

# Global import manager instance
imports = ImportManager()

# Convenience functions
def numpy_available() -> bool:
    return imports._numpy is not None

def scipy_available() -> bool:
    return imports._scipy is not None

def torch_available() -> bool:
    return imports._torch is not None

def tensorflow_available() -> bool:
    return imports._tensorflow is not None