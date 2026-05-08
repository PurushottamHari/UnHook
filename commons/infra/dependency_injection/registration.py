import importlib
import pkgutil
from typing import List

from injector import Binder

from .injectable import _REGISTRY


def discover_and_register_injectables(
    binder: Binder, package_name: str, exclude_packages: List[str] = None
):
    """
    Scans the given package for classes decorated with @injectable and binds them.
    This centralized helper ensures that all services use the same discovery logic.
    """
    if exclude_packages is None:
        exclude_packages = ["tests"]

    # Import the root package to start the scan
    try:
        root_package = importlib.import_module(package_name)
    except ModuleNotFoundError:
        print(f"⚠️ [DI] Package '{package_name}' not found for discovery.")
        return

    # Walk through all submodules to trigger @injectable decorators
    prefix = root_package.__name__ + "."
    if hasattr(root_package, "__path__"):
        for _, module_name, _ in pkgutil.walk_packages(root_package.__path__, prefix):
            # Skip excluded packages
            if any(
                module_name.startswith(prefix + ex.strip("."))
                or module_name == prefix + ex.strip(".")
                for ex in exclude_packages
            ):
                continue

            try:
                importlib.import_module(module_name)
            except Exception:
                # Skip modules that fail to import
                continue

    # Bind everything found in the global registry
    registered_count = 0
    for cls, scope in _REGISTRY:
        binder.bind(cls, to=cls, scope=scope)
        registered_count += 1

    if registered_count > 0:
        print(
            f"✅ [DI] Registered {registered_count} injectable classes from '{package_name}'."
        )
