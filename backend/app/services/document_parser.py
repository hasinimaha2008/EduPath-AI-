import os
import re
from typing import List, Dict, Any, Tuple
import fitz  # PyMuPDF
import docx

class DocumentParserService:
    CHUNK_SIZE = 800  # characters per chunk approximate
    CHUNK_OVERLAP = 150

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text from PDF, returning a list of dicts with page_number and text.
        """
        pages = []
        doc = fitz.open(file_path)
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            text = page.get_text("text")
            if text and text.strip():
                pages.append({
                    "page_number": page_idx + 1,
                    "text": text.strip()
                })
        doc.close()
        return pages

    @staticmethod
    def extract_text_from_docx(file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text from DOCX, grouping paragraphs by page estimates.
        """
        doc = docx.Document(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
        
        # Approximate 5 paragraphs per page for docx
        pages = []
        current_page_text = []
        page_num = 1
        
        for i, p in enumerate(paragraphs):
            current_page_text.append(p)
            if len(current_page_text) >= 5 or i == len(paragraphs) - 1:
                pages.append({
                    "page_number": page_num,
                    "text": "\n\n".join(current_page_text)
                })
                current_page_text = []
                page_num += 1

        return pages

    @classmethod
    def chunk_document(cls, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes page-indexed text and chunks it semantically, preserving page citations.
        """
        chunks = []
        chunk_idx = 0

        for page in pages:
            page_num = page["page_number"]
            page_text = page["text"]
            
            # Clean excessive whitespaces
            cleaned = re.sub(r'\s+', ' ', page_text).strip()
            
            if len(cleaned) <= cls.CHUNK_SIZE:
                chunks.append({
                    "chunk_index": chunk_idx,
                    "page_number": page_num,
                    "content": cleaned,
                    "token_count": len(cleaned.split())
                })
                chunk_idx += 1
            else:
                start = 0
                while start < len(cleaned):
                    end = start + cls.CHUNK_SIZE
                    # Try to break at a sentence boundary if possible
                    if end < len(cleaned):
                        match = re.search(r'([.?!]\s+)', cleaned[start:end])
                        if match and match.start() > cls.CHUNK_SIZE // 2:
                            end = start + match.end()
                    
                    sub_text = cleaned[start:end].strip()
                    if sub_text:
                        chunks.append({
                            "chunk_index": chunk_idx,
                            "page_number": page_num,
                            "content": sub_text,
                            "token_count": len(sub_text.split())
                        })
                        chunk_idx += 1
                    
                    start += cls.CHUNK_SIZE - cls.CHUNK_OVERLAP

        return chunks
