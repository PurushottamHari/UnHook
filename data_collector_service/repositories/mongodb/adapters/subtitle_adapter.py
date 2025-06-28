from typing import Dict, Optional

from data_collector_service.collectors.youtube.models.subtitles import Subtitles, SubtitleData, SubtitleInfo
from data_collector_service.repositories.mongodb.models.subtitle_db_model import SubtitleDB, SubtitleInfoDB


class SubtitleDBAdapter:
    @staticmethod
    def to_db_model(subtitles: Optional[Subtitles]) -> Optional[SubtitleDB]:
        if not subtitles:
            return None

        automatic_db = {lang: SubtitleInfoDB.from_dict(info.to_dict())
                        for lang, info in subtitles.automatic.items()}
        manual_db = {lang: SubtitleInfoDB.from_dict(info.to_dict())
                     for lang, info in subtitles.manual.items()}

        return SubtitleDB(automatic=automatic_db or None, manual=manual_db or None)

    @staticmethod
    def from_db_model(subtitles_db: Optional[SubtitleDB]) -> Optional[Subtitles]:
        if not subtitles_db:
            return None

        automatic_data = SubtitleData()
        if subtitles_db.automatic:
            for lang, info_db in subtitles_db.automatic.items():
                automatic_data[lang] = SubtitleInfo.from_dict(info_db.to_dict())

        manual_data = SubtitleData()
        if subtitles_db.manual:
            for lang, info_db in subtitles_db.manual.items():
                manual_data[lang] = SubtitleInfo.from_dict(info_db.to_dict())
        
        if not manual_data and not automatic_data:
            return None

        return Subtitles(automatic=automatic_data, manual=manual_data) 