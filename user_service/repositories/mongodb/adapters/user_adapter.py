"""
Adapter for converting between internal User model and MongoDB UserDBModel.
"""
from datetime import datetime
from uuid import UUID
from typing import List
from user_service.models.user import User
from user_service.models.interests import Interest, NotInterested
from user_service.models.manual_config import ManualConfig
from user_service.models.youtube_config import YoutubeConfig, YoutubeChannelConfig
from user_service.models.enums import CategoryName, Weekday, OutputType
from ..models.user_db_model import UserDBModel
from ..models.interests_db_model import InterestDBModel, NotInterestedDBModel
from ..models.manual_config_db_model import ManualConfigDBModel
from ..models.youtube_config_db_model import YoutubeConfig as YoutubeConfigDBModel, YoutubeChannelConfig as YoutubeChannelConfigDBModel

class UserAdapter:
    """Adapter for converting between User and UserDBModel."""
    
    @staticmethod
    def _to_interest_db_model(interest: Interest) -> InterestDBModel:
        """Convert internal Interest to InterestDBModel."""
        return InterestDBModel(
            category_name=interest.category_name.value,
            category_definition=interest.category_definition,
            weekdays=[day.value for day in interest.weekdays],
            output_type=interest.output_type.value
        )
    
    @staticmethod
    def _to_not_interested_db_model(not_interested: NotInterested) -> NotInterestedDBModel:
        """Convert internal NotInterested to NotInterestedDBModel."""
        return NotInterestedDBModel(
            category_definition=not_interested.category_definition
        )
    
    @staticmethod
    def _to_youtube_channel_config_db_model(config: YoutubeChannelConfig) -> YoutubeChannelConfigDBModel:
        """Convert internal YoutubeChannelConfig to YoutubeChannelConfigDBModel."""
        return YoutubeChannelConfigDBModel(
            channel_id=config.channel_id,
            max_videos_daily=config.max_videos_daily,
            not_interested=[UserAdapter._to_not_interested_db_model(n) for n in config.not_interested] if config.not_interested else None,
            output_type=config.output_type.value
        )
    
    @staticmethod
    def _to_youtube_config_db_model(config: YoutubeConfig) -> YoutubeConfigDBModel:
        """Convert internal YoutubeConfig to YoutubeConfigDBModel."""
        return YoutubeConfigDBModel(
            discover_on=config.discover_on,
            channels=[UserAdapter._to_youtube_channel_config_db_model(c) for c in config.channels]
        )
    
    @staticmethod
    def _to_manual_config_db_model(config: ManualConfig) -> ManualConfigDBModel:
        """Convert internal ManualConfig to ManualConfigDBModel."""
        return ManualConfigDBModel(
            youtube=UserAdapter._to_youtube_config_db_model(config.youtube)
        )
    
    @staticmethod
    def _to_interest_model(db_model: InterestDBModel) -> Interest:
        """Convert InterestDBModel to internal Interest."""
        return Interest(
            category_name=CategoryName(db_model.category_name),
            category_definition=db_model.category_definition,
            weekdays=[Weekday(day) for day in db_model.weekdays],
            output_type=OutputType(db_model.output_type)
        )
    
    @staticmethod
    def _to_not_interested_model(db_model: NotInterestedDBModel) -> NotInterested:
        """Convert NotInterestedDBModel to internal NotInterested."""
        return NotInterested(
            category_definition=db_model.category_definition
        )
    
    @staticmethod
    def _to_youtube_channel_config_model(db_model: YoutubeChannelConfigDBModel) -> YoutubeChannelConfig:
        """Convert YoutubeChannelConfigDBModel to internal YoutubeChannelConfig."""
        return YoutubeChannelConfig(
            channel_id=db_model.channel_id,
            max_videos_daily=db_model.max_videos_daily,
            not_interested=[UserAdapter._to_not_interested_model(n) for n in db_model.not_interested] if db_model.not_interested else [],
            output_type=OutputType(db_model.output_type)
        )
    
    @staticmethod
    def _to_youtube_config_model(db_model: YoutubeConfigDBModel) -> YoutubeConfig:
        """Convert YoutubeConfigDBModel to internal YoutubeConfig."""
        return YoutubeConfig(
            discover_on=db_model.discover_on,
            channels=[UserAdapter._to_youtube_channel_config_model(c) for c in db_model.channels]
        )
    
    @staticmethod
    def _to_manual_config_model(db_model: ManualConfigDBModel) -> ManualConfig:
        """Convert ManualConfigDBModel to internal ManualConfig."""
        return ManualConfig(
            youtube=UserAdapter._to_youtube_config_model(db_model.youtube)
        )
    
    @staticmethod
    def to_db_model(user: User) -> UserDBModel:
        """Convert internal User model to MongoDB UserDBModel."""
        return UserDBModel(
            id=str(user.id),
            email=user.email,
            name=user.name,
            created_at=user.created_at.isoformat() + 'Z',
            max_reading_time_per_day_mins=user.max_reading_time_per_day_mins,
            interested=[UserAdapter._to_interest_db_model(i) for i in user.interested],
            not_interested=[UserAdapter._to_not_interested_db_model(n) for n in user.not_interested],
            manual_configs=UserAdapter._to_manual_config_db_model(user.manual_configs)
        )
    
    @staticmethod
    def to_internal_model(db_model: UserDBModel) -> User:
        """Convert MongoDB UserDBModel to internal User model."""
        return User(
            id=UUID(db_model.id),
            email=db_model.email,
            name=db_model.name,
            created_at=datetime.fromisoformat(db_model.created_at[:-1]),
            max_reading_time_per_day_mins=db_model.max_reading_time_per_day_mins,
            interested=[UserAdapter._to_interest_model(i) for i in db_model.interested],
            not_interested=[UserAdapter._to_not_interested_model(n) for n in db_model.not_interested],
            manual_configs=UserAdapter._to_manual_config_model(db_model.manual_configs)
        ) 