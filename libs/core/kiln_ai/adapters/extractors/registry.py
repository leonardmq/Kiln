from kiln_ai.adapters.extractors.base_extractor import BaseExtractor
from kiln_ai.adapters.extractors.docling_extractor import DoclingExtractor
from kiln_ai.adapters.extractors.markitdown_extractor import MarkitdownExtractor
from kiln_ai.datamodel.file import ExtractorType
from kiln_ai.utils.exhaustive_error import raise_exhaustive_enum_error


def extractor_adapter_from_type(extractor_type: ExtractorType) -> type[BaseExtractor]:
    match extractor_type:
        case ExtractorType.docling:
            return DoclingExtractor
        case ExtractorType.markitdown:
            return MarkitdownExtractor
        case _:
            # type checking will catch missing cases
            raise_exhaustive_enum_error(extractor_type)
