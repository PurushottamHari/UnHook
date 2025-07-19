from typing import Dict, Optional

import langcodes

from data_collector_service.collectors.youtube.models.subtitles import (
    SubtitleData, SubtitleInfo, Subtitles)


class SubtitleAdapter:
    @staticmethod
    def from_enrich_dict(enrich_details_dict: Dict) -> Optional[Subtitles]:
        """
        Creates a Subtitles object from the 'subtitles' and 'automatic_captions'
        keys in the enrich_details_dict from yt-dlp for English and Hindi.

        Args:
            enrich_details_dict: Dictionary with video details from yt-dlp.

        Returns:
            An optional Subtitles object.
        """
        manual_subtitles_raw = enrich_details_dict.get("subtitles")
        automatic_subtitles_raw = enrich_details_dict.get("automatic_captions")

        if not manual_subtitles_raw and not automatic_subtitles_raw:
            return None

        target_languages = {"en", "hi"}

        manual_subtitle_data = SubtitleData()
        if manual_subtitles_raw:
            for lang, subs in manual_subtitles_raw.items():
                try:
                    language_code = langcodes.get(lang).language
                    if language_code in target_languages:
                        if subs and isinstance(subs, list):
                            sub_info_map = {
                                sub["ext"]: sub["url"]
                                for sub in subs
                                if sub.get("ext") and sub.get("url")
                            }
                            if sub_info_map:
                                manual_subtitle_data[language_code] = (
                                    SubtitleInfo.from_dict(sub_info_map)
                                )
                except (ValueError, langcodes.exceptions.LanguageTagError):
                    # Invalid language code, skip it
                    print("Invalid language code?: " + lang)
                    pass

        automatic_subtitle_data = SubtitleData()
        if automatic_subtitles_raw:
            for lang, subs in automatic_subtitles_raw.items():
                try:
                    language_code = langcodes.get(lang).language
                    if language_code in target_languages:
                        if subs and isinstance(subs, list):
                            sub_info_map = {
                                sub["ext"]: sub["url"]
                                for sub in subs
                                if sub.get("ext") and sub.get("url")
                            }
                            if sub_info_map:
                                automatic_subtitle_data[language_code] = (
                                    SubtitleInfo.from_dict(sub_info_map)
                                )
                except (ValueError, langcodes.exceptions.LanguageTagError):
                    # Invalid language code, skip it
                    pass

        if not manual_subtitle_data and not automatic_subtitle_data:
            return None

        subtitles_obj = Subtitles(
            automatic=automatic_subtitle_data, manual=manual_subtitle_data
        )
        return subtitles_obj
