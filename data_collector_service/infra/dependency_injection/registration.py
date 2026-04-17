import importlib
import pkgutil
from typing import List, Tuple, Type
from injector import Binder, singleton, Scope, Module, provider, Injector
from data_collector_service.config.config import Config
from data_collector_service.repositories.mongodb.user_collected_content_repository import (
    MongoDBUserCollectedContentRepository,
)
from data_collector_service.repositories.user_collected_content_repository import (
    UserCollectedContentRepository,
)
from data_collector_service.repositories.mongodb.config.database import MongoDB

from .injectable import _REGISTRY


class DataCollectorModule(Module):
    def configure(self, binder: Binder) -> None:
        # Repositories (Manual bindings for abstract interfaces)
        binder.bind(
            UserCollectedContentRepository,
            to=MongoDBUserCollectedContentRepository,
            scope=singleton,
        )

        # Automatically discover and bind all classes decorated with @injectable
        _discover_and_register_injectables(binder, "data_collector_service")

    @provider
    @singleton
    def provide_config(self) -> Config:
        return Config()

    @provider
    @singleton
    def provide_mongodb(self) -> MongoDB:
        """
        Provides a MongoDB instance, ensuring connection is established.
        """
        MongoDB.connect_to_database()
        return MongoDB()


def create_injector() -> Injector:
    return Injector([DataCollectorModule()])


def _discover_and_register_injectables(
    binder: Binder, package_name: str, exclude_packages: List[str] = None
):
    """
    Scans the given package for classes decorated with @injectable and binds them.
    """
    if exclude_packages is None:
        exclude_packages = ["tests"]

    # Import the root package
    try:
        root_package = importlib.import_module(package_name)
    except ModuleNotFoundError:
        return

    # Walk through all submodules to trigger decorators
    prefix = root_package.__name__ + "."
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
            # Skip modules that fail to import (might be due to missing dependencies in certain environments)
            continue

    # Bind everything in the registry
    for cls, scope in _REGISTRY:
        binder.bind(cls, to=cls, scope=scope)
