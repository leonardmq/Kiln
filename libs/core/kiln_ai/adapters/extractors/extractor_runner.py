class ExtractorRunner:
    def __init__(self, extractor: BaseExtractor):
        self.extractor = extractor

    def run(self, file: File) -> str:
        return self.extractor.extract(file)
