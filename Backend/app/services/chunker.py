from langchain_text_splitters import RecursiveCharacterTextSplitter

class TranscriptChunker:

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50
        )

    def chunk(self, text: str):
        return self.splitter.split_text(text)
