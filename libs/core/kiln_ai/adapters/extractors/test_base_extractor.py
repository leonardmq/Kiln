import tempfile
from unittest.mock import patch

import pytest

from kiln_ai.adapters.extractors.base_extractor import (
    BaseExtractor,
    BaseExtractorConfig,
    ExtractionFormat,
    ExtractionResult,
    FileInfo,
    FileInfoTrusted,
)


class MockBaseExtractor(BaseExtractor):
    def _extract(
        self, file_info: FileInfo, custom_prompt: str | None
    ) -> ExtractionResult:
        return ExtractionResult(
            is_passthrough=False,
            content="mock concrete extractor output",
            content_format=ExtractionFormat.MARKDOWN,
        )


@pytest.fixture
def mock_extractor():
    return MockBaseExtractor(BaseExtractorConfig())


def mock_extractor_with_passthroughs(mimetypes: list[str]):
    return MockBaseExtractor(BaseExtractorConfig(passthrough_mimetypes=mimetypes))


def test_load_file_bytes(mock_extractor):
    # write a test file to the temp directory
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"test")
        temp_file_path = temp_file.name
    assert mock_extractor._load_file_bytes(temp_file_path) == b"test"


def test_load_file_bytes_failure(mock_extractor):
    with patch(
        "kiln_ai.adapters.extractors.base_extractor.file_utils.load_file_bytes",
        side_effect=Exception,
    ):
        with pytest.raises(ValueError):
            mock_extractor._load_file_bytes("nonexistent.txt")


def test_load_file_text(mock_extractor):
    # write a test file to the temp directory
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"test")
        temp_file_path = temp_file.name
    assert mock_extractor._load_file_text(temp_file_path) == "test"


def test_load_file_text_failure(mock_extractor):
    with patch(
        "kiln_ai.adapters.extractors.base_extractor.file_utils.load_file_text",
        side_effect=Exception,
    ):
        with pytest.raises(ValueError):
            mock_extractor._load_file_text("nonexistent.txt")


# parametrize for txt -> text/plain, png -> image/png, etc.
@pytest.mark.parametrize(
    "path, expected_mime_type",
    [
        ("test.txt", "text/plain"),
        ("test.png", "image/png"),
        ("test.pdf", "application/pdf"),
    ],
)
def test_get_mime_type(mock_extractor, path: str, expected_mime_type: str):
    assert mock_extractor._get_mime_type(path) == expected_mime_type


def test_get_mime_type_failure(mock_extractor):
    with patch(
        "kiln_ai.adapters.extractors.base_extractor.file_utils.get_mime_type",
        side_effect=Exception,
    ):
        with pytest.raises(ValueError):
            mock_extractor._get_mime_type("nonexistent.some-unknown-file-type")


def test_should_passthrough():
    extractor = MockBaseExtractor(
        BaseExtractorConfig(
            passthrough_mimetypes=[
                "text/plain",
                "text/markdown",
            ]
        )
    )

    # should passthrough
    assert extractor._should_passthrough("text/plain")
    assert extractor._should_passthrough("text/markdown")

    # should not passthrough
    assert not extractor._should_passthrough("image/png")
    assert not extractor._should_passthrough("application/pdf")
    assert not extractor._should_passthrough("text/html")
    assert not extractor._should_passthrough("image/jpeg")


def test_extract_passthrough():
    """Test that passthrough files skip _extract() and return file contents directly"""
    extractor = mock_extractor_with_passthroughs(["text/plain", "text/markdown"])
    with (
        patch.object(
            extractor,
            "_extract",
            return_value=ExtractionResult(
                is_passthrough=False,
                content="mock concrete extractor output",
                content_format=ExtractionFormat.MARKDOWN,
            ),
        ) as mock_extract,
        patch.object(extractor, "_load_file_text", return_value="test content"),
        patch.object(extractor, "_get_mime_type", return_value="text/plain"),
    ):
        result = extractor.extract(
            file_info=FileInfo(path="test.txt"), custom_prompt=None
        )

        # Verify _extract was not called
        mock_extract.assert_not_called()

        # Verify correct passthrough result
        assert result.is_passthrough == True
        assert result.content == "test content"
        assert result.content_format == ExtractionFormat.TEXT


@pytest.mark.parametrize(
    "path, mime_type",
    [
        ("test.mp3", "audio/mpeg"),
        ("test.png", "image/png"),
        ("test.pdf", "application/pdf"),
    ],
)
def test_extract_non_passthrough(path: str, mime_type: str):
    """Test that non-passthrough files call _extract() on the subclass and return the result"""
    extractor = mock_extractor_with_passthroughs(["text/plain", "text/markdown"])

    with (
        patch.object(
            extractor,
            "_extract",
            return_value=ExtractionResult(
                is_passthrough=False,
                content="mock concrete extractor output",
                content_format=ExtractionFormat.MARKDOWN,
            ),
        ) as mock_extract,
        patch.object(extractor, "_get_mime_type", return_value=mime_type),
    ):
        # first we call the base class extract method
        result = extractor.extract(file_info=FileInfo(path=path), custom_prompt=None)

        # then we call the subclass _extract method and add validated mime_type
        mock_extract.assert_called_once_with(
            FileInfoTrusted(path=path, mime_type=mime_type), None
        )

        assert result.is_passthrough == False
        assert result.content == "mock concrete extractor output"
        assert result.content_format == ExtractionFormat.MARKDOWN
