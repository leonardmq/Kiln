from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Union

from pydantic import Field

from kiln_ai.datamodel.basemodel import ID_TYPE, KilnParentedModel, KilnParentModel

if TYPE_CHECKING:
    from kiln_ai.datamodel.project import Project


class ExtractorType(str, Enum):
    docling = "docling"
    markitdown = "markitdown"


class Extraction(KilnParentedModel):
    extractor_type: ExtractorType = Field(description="The type of extractor to use.")
    file_id: ID_TYPE = Field(description="The id of the file to extract data from.")
    text: str = Field(description="The text extracted from the file.")


class ExtractorConfig(
    KilnParentedModel, KilnParentModel, parent_of={"extractions": Extraction}
):
    extractor_type: ExtractorType = Field(
        description="The type of extractor used to extract the data from the file.",
    )

    properties: dict[str, Any] = Field(
        default={},
        description="Properties to be used to execute the extraction. This is config_type specific and should serialize to a json dict.",
    )


class File(
    KilnParentedModel, KilnParentModel, parent_of={"extractor_configs": ExtractorConfig}
):
    name: str = Field(description="The name of the file.")
    name_original: str = Field(
        description="The original name of the file when uploaded."
    )
    mime_type: str = Field(description="The mime type of the file.")
    file_path: str = Field(description="The path to the file.")
    size: int = Field(description="The size of the file in bytes.")
    hash: str = Field(description="The hash of the file.")
    extension: str = Field(description="The extension of the file.")

    # Workaround to return typed parent without importing Project
    def parent_project(self) -> "Project":
        if self.parent is None or self.parent.__class__.__name__ != "Project":
            raise ValueError("parent must be a Project")
        return self.parent  # type: ignore
