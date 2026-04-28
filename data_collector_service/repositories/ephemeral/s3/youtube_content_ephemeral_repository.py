import logging

import boto3
from botocore.config import Config as BotoConfig
from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.config.config import Config
from data_collector_service.models.youtube.subtitle_models import (
    SubtitleData, SubtitleMap)
from data_collector_service.repositories.youtube_content_ephemeral_repository import (
    SubtitleFileType, YoutubeContentEphemeralRepository)

logger = logging.getLogger(__name__)


@injectable()
class S3YoutubeContentEphemeralRepository(YoutubeContentEphemeralRepository):
    """
    S3/R2 implementation of YoutubeContentEphemeralRepository.
    """

    @inject
    def __init__(self, config: Config):
        self.config = config
        self.bucket_name = config.s3_bucket_name

        # Boto3 client setup for R2/S3
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=config.s3_endpoint_url,
            aws_access_key_id=config.s3_access_key_id,
            aws_secret_access_key=config.s3_secret_access_key,
            config=BotoConfig(
                signature_version="s3v4", s3={"addressing_style": "path"}
            ),
            region_name="auto",  # Cloudflare R2 uses "auto"
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """
        Checks if the bucket exists and creates it if it doesn't.
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except Exception as e:
            error_code = ""
            if hasattr(e, "response"):
                error_code = str(e.response.get("Error", {}).get("Code", ""))

            # 404: Not Found
            # 400: Bad Request (sometimes returned by S3-compatible APIs if addressing is weird)
            if error_code in ["404", "400"]:
                logger.info(
                    f"Bucket {self.bucket_name} not found or inaccessible (code {error_code}). Creating it..."
                )
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Bucket {self.bucket_name} created successfully.")
                except Exception as create_error:
                    # Check if it failed because it already exists (race condition or false positive on 400)
                    error_msg = str(create_error)
                    if (
                        "BucketAlreadyOwnedByYou" in error_msg
                        or "BucketAlreadyExists" in error_msg
                    ):
                        logger.info(f"Bucket {self.bucket_name} already exists.")
                    else:
                        logger.error(
                            f"Failed to create bucket {self.bucket_name}: {create_error}"
                        )
                        raise
            else:
                logger.error(f"Error checking bucket {self.bucket_name}: {e}")
                raise

    def _generate_s3_key(
        self,
        video_id: str,
        subtitle_type: str,
        extension: str,
        file_type: SubtitleFileType,
        language: str,
    ) -> str:
        """
        Generates the S3 key (path) for a subtitle file using a folder-first structure.
        Format: {video_id}/{file_type}/{subtitle_type}/{language}.{extension}
        """
        return f"{video_id}/{file_type.value}/{subtitle_type}/{language}.{extension}"

    def store_subtitles(
        self,
        video_id: str,
        subtitles: str,
        extension: str,
        subtitle_type: str,
        language: str,
    ):
        """
        Stores the downloaded subtitles in S3.
        """
        if subtitles is None:
            raise ValueError(
                f"Cannot store None subtitles for video {video_id} (Type: {subtitle_type}, Language: {language}, Ext: {extension})"
            )

        key = self._generate_s3_key(
            video_id, subtitle_type, extension, SubtitleFileType.DOWNLOADED, language
        )
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=subtitles.encode("utf-8"),
            ContentType="text/plain",
        )

    def store_clean_subtitles(
        self,
        video_id: str,
        subtitles: str,
        extension: str,
        subtitle_type: str,
        language: str,
    ):
        """
        Stores the cleaned subtitles in S3.
        """
        if subtitles is None:
            raise ValueError(
                f"Cannot store None clean subtitles for video {video_id} (Type: {subtitle_type}, Language: {language}, Ext: {extension})"
            )

        key = self._generate_s3_key(
            video_id, subtitle_type, extension, SubtitleFileType.CLEAN, language
        )
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=subtitles.encode("utf-8"),
            ContentType="text/plain",
        )

    def get_clean_subtitle_file_data(
        self, video_id: str, extension: str, subtitle_type: str, language: str
    ) -> str:
        """
        Gets the cleaned subtitles from S3.
        """
        key = self._generate_s3_key(
            video_id, subtitle_type, extension, SubtitleFileType.CLEAN, language
        )
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response["Body"].read().decode("utf-8")
        except self.s3_client.exceptions.NoSuchKey:
            raise RuntimeError(f"Subtitle file not found in S3 at {key}")

    def get_downloaded_subtitle_file_data(
        self, video_id: str, extension: str, subtitle_type: str, language: str
    ) -> str:
        """
        Gets the downloaded subtitles from S3.
        """
        key = self._generate_s3_key(
            video_id, subtitle_type, extension, SubtitleFileType.DOWNLOADED, language
        )
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response["Body"].read().decode("utf-8")
        except self.s3_client.exceptions.NoSuchKey:
            raise RuntimeError(f"Subtitle file not found in S3 at {key}")

    def do_any_subtitles_exist_for_video(self, video_id: str) -> bool:
        """
        Checks if any downloaded subtitles exist for a given video ID in S3.
        """
        return self._check_if_any_objects_exist_under_prefix(
            f"{video_id}/{SubtitleFileType.DOWNLOADED.value}/"
        )

    def do_any_clean_subtitles_exist_for_video(self, video_id: str) -> bool:
        """
        Checks if any cleaned subtitles exist for a given video ID in S3.
        """
        return self._check_if_any_objects_exist_under_prefix(
            f"{video_id}/{SubtitleFileType.CLEAN.value}/"
        )

    def _check_if_any_objects_exist_under_prefix(self, prefix: str) -> bool:
        """
        Checks if any keys with the given prefix exist. Efficiently uses pagination and returns on first item.
        """
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=prefix, MaxKeys=1
        )
        return "Contents" in response

    def check_if_downloaded_subtitle_file_exists(
        self, video_id: str, extension: str, subtitle_type: str, language: str
    ) -> bool:
        key = self._generate_s3_key(
            video_id, subtitle_type, extension, SubtitleFileType.DOWNLOADED, language
        )
        return self._key_exists(key)

    def check_if_clean_subtitle_file_exists(
        self, video_id: str, extension: str, subtitle_type: str, language: str
    ) -> bool:
        key = self._generate_s3_key(
            video_id, subtitle_type, extension, SubtitleFileType.CLEAN, language
        )
        return self._key_exists(key)

    def _key_exists(self, key: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except:
            return False

    def get_all_clean_subtitle_file_data(self, video_id: str) -> SubtitleData:
        automatic_subtitle_maps = []
        manual_subtitle_maps = []

        # We only search under the 'clean_subtitles' folder for this video
        prefix = f"{video_id}/{SubtitleFileType.CLEAN.value}/"
        paginator = self.s3_client.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
            if "Contents" in page:
                for obj in page["Contents"]:
                    key = obj["Key"]
                    # Key format: {video_id}/{file_type}/{subtitle_type}/{language}.{extension}
                    parts = key.split("/")
                    if len(parts) >= 4:
                        subtitle_type = parts[2]
                        # language is part of the filename: {language}.{extension}
                        filename = parts[3]
                        language = filename.split(".")[0]

                        response = self.s3_client.get_object(
                            Bucket=self.bucket_name, Key=key
                        )
                        subtitle_content = response["Body"].read().decode("utf-8")

                        sub_map = SubtitleMap(
                            language=language, subtitle=subtitle_content
                        )
                        if subtitle_type == "automatic":
                            automatic_subtitle_maps.append(sub_map)
                        else:
                            manual_subtitle_maps.append(sub_map)

        return SubtitleData(
            automatic=automatic_subtitle_maps, manual=manual_subtitle_maps
        )
