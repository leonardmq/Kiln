import logging
from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel, Field

import kiln_ai.adapters.extractors.file_utils as file_utils

logger = logging.getLogger(__name__)


class BaseExtractorConfig(BaseModel):
    """
    Base class for all extractor configs.
    """

    passthrough_mimetypes: list[str] = Field(
        default_factory=list,
        description="If the mimetype is in this list, the extractor will not be used and the file will be returned as is. For example, if the file is a text file, the extracted data is just itself.",
    )


class ExtractionFormat(str, Enum):
    TEXT = "text"
    MARKDOWN = "markdown"


# TODO: take in the file/document datamodel instead once we have it
class FileInfo(BaseModel):
    # TODO: check if works with relative paths or needs to be absolute
    path: str = Field(description="The path to the file to extract from.")


class FileInfoTrusted(FileInfo):
    mime_type: str = Field(description="The mime type of the file to extract from.")


class ExtractionResult(BaseModel):
    is_passthrough: bool = Field(
        default=False, description="Whether the extractor returned the file as is."
    )
    content_format: ExtractionFormat = Field(
        description="The format of the extracted data."
    )
    content: str = Field(description="The extracted data.")


class BaseExtractor(ABC):
    """
    Base class for all extractors.

    Should be subclassed, and the _extract method implemented.
    """

    def __init__(self, config: BaseExtractorConfig):
        self.config = config

    @abstractmethod
    def _extract(self, file_info: FileInfo, prompt: str | None) -> ExtractionResult:
        pass

    def extract(
        self, file_info: FileInfoTrusted, custom_prompt: str | None
    ) -> ExtractionResult:
        try:
            mime_type = self._get_mime_type(file_info.path)
            if self._should_passthrough(mime_type):
                content_format = (
                    ExtractionFormat.MARKDOWN
                    if mime_type == "text/markdown"
                    else ExtractionFormat.TEXT
                )

                return ExtractionResult(
                    is_passthrough=True,
                    content=self._load_file_text(file_info.path),
                    content_format=content_format,
                )
            return self._extract(
                FileInfoTrusted(
                    path=file_info.path,
                    mime_type=mime_type,
                ),
                custom_prompt,
            )
        except Exception as e:
            # TODO: wrap / handle errors
            # - provider error -> get the error message from the provider
            # - other errors -> return a general error message
            raise e

    def _should_passthrough(self, mime_type: str) -> bool:
        """
        Whether the extractor should return the file as is.
        """
        return mime_type in self.config.passthrough_mimetypes

    def _load_file_bytes(self, path: str) -> bytes:
        try:
            return file_utils.load_file_bytes(path)
        except Exception as e:
            raise ValueError(f"Error loading file bytes for {path}: {e}")

    def _load_file_text(self, path: str) -> str:
        try:
            return file_utils.load_file_text(path)
        except Exception as e:
            raise ValueError(f"Error loading file text for {path}: {e}")

    def _get_mime_type(self, path: str) -> str:
        # NOTE: maybe we will already have the mimetype from the datamodel? but not sure
        # we would trust it anyway in the extractor, will need to check
        try:
            return file_utils.get_mime_type(path)
        except Exception as e:
            raise ValueError(f"Error getting mime type for {path}: {e}")
