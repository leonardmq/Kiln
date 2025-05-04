from kiln_ai.adapters.extractors.base_extractor import BaseExtractor
from kiln_ai.datamodel.file import File


class DoclingExtractor(BaseExtractor):
    """
    An extractor that extracts data from a docling file.
    """

    def _extract(self, file: File) -> str:
        return "content of the file extracted by docling"
