"""Compatibility shim: stable import path for ProjectXClient."""
from .client import ProjectXClient  # re-export
__all__ = ["ProjectXClient"]

