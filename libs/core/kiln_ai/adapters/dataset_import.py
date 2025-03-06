import csv
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Protocol

from pydantic import BaseModel, Field, field_validator

from kiln_ai.datamodel import DataSource, DataSourceType, Task, TaskOutput, TaskRun


class DatasetImportFormat(str, Enum):
    """
    The format of the dataset to import.
    """

    CSV = "csv"


class DatasetFileImporter(Protocol):
    """Protocol for dataset importers"""

    def __call__(
        self,
        dataset_path: str,
    ) -> int: ...


class CSVRowSchema(BaseModel):
    """Schema for validating rows in a CSV file."""

    input: str  # The input to the model
    output: str  # The output of the model
    reasoning: str = Field(default=None)  # The reasoning of the model
    tags: list[str] = Field(default_factory=list)  # The tags of the run

    @field_validator("tags", mode="before")
    def split_tags(cls, value):
        # Tags are separated by commas in the CSV
        if isinstance(value, str) and value:
            return value.split(",")
        return []


def import_csv(task: Task, dataset_path: str, dataset_name: str) -> int:
    """Import a CSV dataset"""
    imported_runs = 0
    with open(dataset_path, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            validated_row = CSVRowSchema(**row)
            run = TaskRun(
                parent=task,
                input=validated_row.input,
                input_source=DataSource(
                    type=DataSourceType.file_import,
                    properties={
                        "file_name": dataset_name,
                    },
                ),
                output=TaskOutput(
                    output=validated_row.output,
                    source=DataSource(
                        type=DataSourceType.file_import,
                        properties={
                            "file_name": dataset_name,
                        },
                    ),
                ),
                intermediate_outputs={
                    "reasoning": validated_row.reasoning,
                },
                tags=validated_row.tags,
            )
            run.save_to_file()
            imported_runs += 1
    return imported_runs


DATASET_IMPORTERS: Dict[DatasetImportFormat, DatasetFileImporter] = {
    DatasetImportFormat.CSV: import_csv,
}


@dataclass
class ImportConfig:
    """Configuration for importing a dataset"""

    dataset_type: DatasetImportFormat
    dataset_path: str
    dataset_name: str


class DatasetFileImporter:
    """Import a dataset from a file"""

    def __init__(self, task: Task, config: ImportConfig):
        self.task = task
        self.dataset_type = config.dataset_type
        self.dataset_path = config.dataset_path
        self.dataset_name = config.dataset_name

    def create_runs_from_file(self) -> int:
        fn = DATASET_IMPORTERS[self.dataset_type]
        return fn(self.task, self.dataset_path, self.dataset_name)
