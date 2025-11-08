"""
BSEE Utilities Package

This package contains utility modules for the Binary Structure Exploration Engine,
including error handling, logging, and other common utilities.
"""

from .error_handler import GlobalErrorHandler, ErrorCategory

__all__ = ['GlobalErrorHandler', 'ErrorCategory']