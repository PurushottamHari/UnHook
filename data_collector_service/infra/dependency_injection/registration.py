import importlib
import pkgutil
from typing import List, Tuple, Type

from injector import Binder, Injector, Module, Scope, provider, singleton

from commons.infra.dependency_injection.registration import \
    discover_and_register_injectables
from commons.messaging.aggregated_schedule.repository import \
    AggregatedScheduleRepository
from commons.messaging.aggregated_schedule.service import \
    AggregatedScheduleService
from data_collector_service.config.config import Config
from data_collector_service.repositories.mongodb.config.database import MongoDB
from data_collector_service.repositories.mongodb.mongodb_aggregated_schedule_repository import \
    MongoDBAggregatedScheduleRepository
from data_collector_service.repositories.mongodb.user_collected_content_repository import \
    MongoDBUserCollectedContentRepository
from data_collector_service.repositories.mongodb.youtube_collected_content_repository import \
    MongoDBYouTubeCollectedContentRepository
from data_collector_service.repositories.user_collected_content_repository import \
    UserCollectedContentRepository
from data_collector_service.repositories.youtube_collected_content_repository import \
    YouTubeCollectedContentRepository


class DataCollectorModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(
            UserCollectedContentRepository,
            to=MongoDBUserCollectedContentRepository,
            scope=singleton,
        )
        binder.bind(
            YouTubeCollectedContentRepository,
            to=MongoDBYouTubeCollectedContentRepository,
            scope=singleton,
        )
        binder.bind(
            AggregatedScheduleRepository,
            to=MongoDBAggregatedScheduleRepository,
            scope=singleton,
        )

        # Automatically discover and bind all classes decorated with @injectable
        discover_and_register_injectables(binder, "commons")
        discover_and_register_injectables(binder, "data_collector_service")

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
