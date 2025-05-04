from kiln_ai.adapters.extractors.base_extractor import BaseExtractor
from kiln_ai.datamodel.file import File


class MarkitdownExtractor(BaseExtractor):
    """
    An extractor that extracts data from a markdown file.
    """

    def _extract(self, file: File) -> str:
        return "content of the file extracted by markitdown"
