"""
Enum classes for user-related data models.
"""

from enum import Enum
from typing import List


class CategoryName(str, Enum):
    TECHNOLOGY = "TECHNOLOGY"
    SCIENCE = "SCIENCE"
    BUSINESS = "BUSINESS"
    HEALTH = "HEALTH"
    COMEDY = "COMEDY"
    SPORTS = "SPORTS"
    NEWS = "NEWS"
    EDUCATION = "EDUCATION"
    ENVIRONMENT = "ENVIRONMENT"
    CULTURE = "CULTURE"
    SPIRITUALITY = "SPIRITUALITY"
    MOVIES = "MOVIES"
    PERSPECTIVES = "PERSPECTIVES"
    GAMING = "GAMING"
    MUSIC = "MUSIC"


class Weekday(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class OutputType(str, Enum):
    VERY_SHORT = "VERY_SHORT"  # One Line update
    SHORT = "SHORT"  # One Paragraph update
    MEDIUM = "MEDIUM"  # One Page update
    LONG = "LONG"  # Detailed Article update
