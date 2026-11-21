import os
import re
from typing import List, Dict, Any, Tuple
import fitz  # PyMuPDF
import docx

class DocumentParserService:
    CHUNK_SIZE = 750  # characters per chunk approximate
    CHUNK_OVERLAP = 120

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

    @staticmethod
    def extract_text_from_txt(file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text from plain text or markdown files.
        """
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Split into ~2000 char pseudo-pages
        pages = []
        lines = content.splitlines()
        current_chunk = []
        current_len = 0
        page_num = 1

        for line in lines:
            current_chunk.append(line)
            current_len += len(line)
            if current_len >= 1800:
                pages.append({
                    "page_number": page_num,
                    "text": "\n".join(current_chunk).strip()
                })
                current_chunk = []
                current_len = 0
                page_num += 1

        if current_chunk:
            pages.append({
                "page_number": page_num,
                "text": "\n".join(current_chunk).strip()
            })

        return pages

    @classmethod
    def chunk_document(cls, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Intelligent chunking preserving headings, paragraphs, and list integrity.
        """
        chunks = []
        chunk_idx = 0

        for page in pages:
            page_num = page["page_number"]
            page_text = page["text"]

            # Split into natural structural blocks (headers or double line breaks)
            raw_blocks = re.split(r'\n\s*\n', page_text)
            blocks = [b.strip() for b in raw_blocks if b.strip()]

            current_chunk_text = ""

            for block in blocks:
                # If adding this block exceeds CHUNK_SIZE and we have text, flush current chunk
                if len(current_chunk_text) + len(block) > cls.CHUNK_SIZE and len(current_chunk_text) > 200:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "page_number": page_num,
                        "content": current_chunk_text.strip(),
                        "token_count": len(current_chunk_text.split())
                    })
                    chunk_idx += 1
                    # Retain last overlap characters
                    overlap_idx = max(0, len(current_chunk_text) - cls.CHUNK_OVERLAP)
                    current_chunk_text = current_chunk_text[overlap_idx:] + " " + block
                else:
                    if current_chunk_text:
                        current_chunk_text += "\n\n" + block
                    else:
                        current_chunk_text = block

            if current_chunk_text.strip():
                chunks.append({
                    "chunk_index": chunk_idx,
                    "page_number": page_num,
                    "content": current_chunk_text.strip(),
                    "token_count": len(current_chunk_text.split())
                })
                chunk_idx += 1

        return chunks
