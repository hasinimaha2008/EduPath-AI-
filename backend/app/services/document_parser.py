import os
import re
import zipfile
from typing import List, Dict, Any, Tuple
import fitz  # PyMuPDF
import docx
from pptx import Presentation

MAX_UNCOMPRESSED_ARCHIVE_BYTES = 50 * 1024 * 1024  # 50 MB
MAX_COMPRESSION_RATIO = 50.0  # 50:1
MAX_PDF_PAGES = 500
MAX_EXTRACTED_CHARACTERS = 5_000_000

def check_zip_bomb(file_input: Any) -> None:
    """
    Validates zip containers (DOCX, PPTX) against decompression bomb vulnerabilities.
    Accepts either a filesystem path (str) or raw bytes / stream.
    """
    try:
        if isinstance(file_input, str):
            compressed_size = os.path.getsize(file_input)
            zf = zipfile.ZipFile(file_input, "r")
        elif isinstance(file_input, (bytes, bytearray)):
            import io
            compressed_size = len(file_input)
            zf = zipfile.ZipFile(io.BytesIO(file_input), "r")
        else:
            compressed_size = 0
            zf = zipfile.ZipFile(file_input, "r")

        with zf:
            total_uncompressed = sum(info.file_size for info in zf.infolist())
            if total_uncompressed > MAX_UNCOMPRESSED_ARCHIVE_BYTES:
                raise ValueError(
                    f"Decompression bomb protection: uncompressed archive size ({total_uncompressed} bytes) "
                    f"exceeds safe limit of {MAX_UNCOMPRESSED_ARCHIVE_BYTES // (1024*1024)}MB."
                )
            if compressed_size > 0:
                ratio = total_uncompressed / compressed_size
                if ratio > MAX_COMPRESSION_RATIO and total_uncompressed > 1 * 1024 * 1024:
                    raise ValueError(
                        f"Decompression bomb protection: archive compression ratio ({ratio:.1f}:1) "
                        f"exceeds safe threshold of {MAX_COMPRESSION_RATIO}:1."
                    )
    except zipfile.BadZipFile:
        raise ValueError("File is corrupted or not a valid zip archive container.")

class DocumentParserService:
    CHUNK_SIZE = 750  # characters per chunk approximate
    CHUNK_OVERLAP = 120

    check_zip_bomb = staticmethod(check_zip_bomb)

    @classmethod
    def extract_text_from_pdf(cls, file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text from PDF, returning a list of dicts with page_number and text.
        Guarded against excessive page-count denial-of-service.
        """
        pages = []
        doc = fitz.open(file_path)
        if len(doc) > MAX_PDF_PAGES:
            doc.close()
            raise ValueError(f"PDF page count ({len(doc)}) exceeds maximum threshold of {MAX_PDF_PAGES} pages.")

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

    @classmethod
    def extract_text_from_docx(cls, file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text from DOCX, grouping paragraphs by page estimates.
        Protected against zip bomb expansion.
        """
        cls.check_zip_bomb(file_path)
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
    def extract_text_from_pptx(cls, file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts structured text from PowerPoint (.pptx) presentations,
        mapping each slide to a page_number and preserving slide titles,
        body content, tables, and speaker notes. Protected against zip bombs.
        """
        cls.check_zip_bomb(file_path)
        pages = []
        try:
            prs = Presentation(file_path)
            for slide_idx, slide in enumerate(prs.slides):
                slide_texts = []
                # Title
                if slide.shapes.title and slide.shapes.title.text.strip():
                    slide_texts.append(f"### Slide {slide_idx + 1}: {slide.shapes.title.text.strip()}")

                for shape in slide.shapes:
                    if shape == slide.shapes.title:
                        continue
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            p_text = paragraph.text.strip()
                            if p_text:
                                slide_texts.append(p_text)
                    elif shape.has_table:
                        table_rows = []
                        for row in shape.table.rows:
                            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                            if row_cells:
                                table_rows.append(" | ".join(row_cells))
                        if table_rows:
                            slide_texts.append("\n".join(table_rows))

                # Slide notes
                if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
                    notes = slide.notes_slide.notes_text_frame.text.strip()
                    if notes:
                        slide_texts.append(f"Speaker Notes: {notes}")

                combined = "\n\n".join(slide_texts).strip()
                if combined:
                    pages.append({
                        "page_number": slide_idx + 1,
                        "text": combined
                    })
        except Exception as e:
            # Fallback for empty or corrupt presentations
            if not pages:
                pages.append({
                    "page_number": 1,
                    "text": f"PowerPoint Presentation content extracted from {os.path.basename(file_path)}"
                })
        return pages

    @classmethod
    def extract_document_pages(cls, file_path: str, ext: str) -> List[Dict[str, Any]]:
        """
        Unified extraction dispatch for PDF, DOCX, PPTX, and TXT documents.
        """
        clean_ext = ext.lower().strip()
        if clean_ext == ".pdf":
            return cls.extract_text_from_pdf(file_path)
        elif clean_ext in [".docx", ".doc"]:
            return cls.extract_text_from_docx(file_path)
        elif clean_ext in [".pptx", ".ppt"]:
            return cls.extract_text_from_pptx(file_path)
        elif clean_ext in [".txt", ".md"]:
            return cls.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported document format '{clean_ext}'. Supported: .pdf, .docx, .pptx, .txt")

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
