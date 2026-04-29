from injector import Binder, Injector, Module, provider, singleton

from commons.infra.dependency_injection.registration import \
    discover_and_register_injectables
from commons.messaging import (BaseCommandRouter, BaseEventRouter,
                               BaseMessagingConfig, MessageConsumer,
                               MessageProducer)
from commons.messaging.aggregated_schedule.repository import \
    AggregatedScheduleRepository
from newspaper_service.config.config import Config
from newspaper_service.messaging.config.messaging_config import MessagingConfig
from newspaper_service.messaging.redis.consumer import RedisMessageConsumer
from newspaper_service.messaging.redis.producer import RedisMessageProducer
from newspaper_service.messaging.routers.command_router import CommandRouter
from newspaper_service.messaging.routers.event_router import EventRouter
from newspaper_service.repositories.generated_content_interaction_repository import \
    GeneratedContentInteractionRepository
from newspaper_service.repositories.generated_content_repository import \
    GeneratedContentRepository
from newspaper_service.repositories.mongodb.config.database import MongoDB
from newspaper_service.repositories.mongodb.generated_content_interaction_repository import \
    MongoDBGeneratedContentInteractionRepository
from newspaper_service.repositories.mongodb.generated_content_repository import \
    MongoDBGeneratedContentRepository
from newspaper_service.repositories.mongodb.mongodb_aggregated_schedule_repository import \
    MongoDBAggregatedScheduleRepository
from newspaper_service.repositories.mongodb.newspaper_repository import \
    MongoDBNewspaperRepository
from newspaper_service.repositories.mongodb.user_collected_content_repository import \
    MongoDBUserCollectedContentRepository
from newspaper_service.repositories.newspaper_repository import \
    NewspaperRepository
from newspaper_service.repositories.user_collected_content_repository import \
    UserCollectedContentRepository


class NewspaperModule(Module):
    def configure(self, binder: Binder) -> None:
        # Repository Bindings
        binder.bind(
            NewspaperRepository,
            to=MongoDBNewspaperRepository,
            scope=singleton,
        )
        binder.bind(
            GeneratedContentRepository,
            to=MongoDBGeneratedContentRepository,
            scope=singleton,
        )
        binder.bind(
            GeneratedContentInteractionRepository,
            to=MongoDBGeneratedContentInteractionRepository,
            scope=singleton,
        )
        binder.bind(
            UserCollectedContentRepository,
            to=MongoDBUserCollectedContentRepository,
            scope=singleton,
        )
        binder.bind(
            AggregatedScheduleRepository,
            to=MongoDBAggregatedScheduleRepository,
            scope=singleton,
        )

        # Messaging Bindings
        binder.bind(BaseMessagingConfig, to=MessagingConfig, scope=singleton)
        binder.bind(MessageConsumer, to=RedisMessageConsumer, scope=singleton)
        binder.bind(MessageProducer, to=RedisMessageProducer, scope=singleton)
        binder.bind(BaseCommandRouter, to=CommandRouter, scope=singleton)
        binder.bind(BaseEventRouter, to=EventRouter, scope=singleton)

        # Automatically discover and bind all classes decorated with @injectable
        discover_and_register_injectables(binder, "commons")
        discover_and_register_injectables(binder, "newspaper_service")

    @provider
    @singleton
    def provide_config(self) -> Config:
        return Config()

    @provider
    @singleton
    def provide_mongodb(self) -> MongoDB:
        """
        Provides a MongoDB instance.
        """
        # newspaper_service database.py handles connection in __new__ or get_database
        return MongoDB()


def create_injector() -> Injector:
    return Injector([NewspaperModule()])
