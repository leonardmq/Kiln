from abc import abstractmethod

from kiln_ai.datamodel.file import File


class BaseExtractor:
    """
    Base class for all evals/evaluators.

    Should be subclassed, and the run_eval method implemented.
    """

    def __init__(self):
        pass

    def extract(self, file: File) -> str:
        return self._extract(file)

    @abstractmethod
    def _extract(self, file: File) -> str:
        """
        Extract data from a file.
        """
        pass
