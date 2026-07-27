import logging
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class TranscriptChunker:
    def __init__(self):
        """
        Initializes the TranscriptChunker with default RecursiveCharacterTextSplitter configurations.
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50
        )

    def chunk(self, text: str) -> List[str]:
        """
        Splits text content into semantic chunks based on chunk size and overlap configurations.
        
        Args:
            text: The text content to split into chunks.
            
        Returns:
            A list of text chunk strings.
        """
        if not text or not isinstance(text, str):
            logger.warning("Empty or non-string input text provided to chunk. Returning empty list.")
            return []
            
        try:
            chunks = self.splitter.split_text(text)
            logger.debug("Successfully split text into %d chunks.", len(chunks))
            return chunks
        except Exception as e:
            logger.exception("Failed to chunk text content.")
            raise e

