"""
Batch Zip Archive & Directory Processor Engine
Extracts, processes, and re-packages multi-file archives (.zip) in parallel.
"""
import io
import zipfile
from pathlib import Path
from pure_text_stripper import PureTextStripper
from pure_image_stripper import PureImageStripper
from metadata_stripper import MetadataStripper
from auto_detector import ContentTypeDetector

class BatchProcessor:
    def __init__(self):
        self.text_engine = PureTextStripper()
        self.image_engine = PureImageStripper()

    def process_zip_archive(self, zip_bytes: bytes) -> tuple[bytes, dict]:
        """
        Reads an input zip file, cleans all text, image, pdf, docx, svg, html, md files inside,
        and returns the cleaned zip archive bytes + summary metrics.
        """
        in_buf = io.BytesIO(zip_bytes)
        out_buf = io.BytesIO()

        files_processed = 0
        cleaned_summary = []

        with zipfile.ZipFile(in_buf, 'r') as zin, zipfile.ZipFile(out_buf, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.is_dir():
                    continue

                raw_bytes = zin.read(item.filename)
                fn = item.filename
                detected_type = ContentTypeDetector.detect_file_type(raw_bytes, fn)

                cleaned_bytes = raw_bytes

                if detected_type == "text":
                    try:
                        text_str = raw_bytes.decode("utf-8")
                        res = self.text_engine.strip_text_watermark(text_str)
                        cleaned_bytes = res["cleaned_text"].encode("utf-8")
                        cleaned_summary.append(f"{fn}: Text cleaned ({res['removal_summary']})")
                    except Exception:
                        pass
                elif detected_type == "image":
                    cleaned_bytes = self.image_engine.strip_image(raw_bytes)
                    cleaned_summary.append(f"{fn}: Image metadata & pixel noise scrubbed")
                elif detected_type == "container":
                    if fn.lower().endswith(".pdf"):
                        cleaned_bytes, _ = MetadataStripper.strip_pdf_metadata(raw_bytes)
                        cleaned_summary.append(f"{fn}: PDF metadata linearized & scrubbed")
                    elif fn.lower().endswith(".docx"):
                        cleaned_bytes, _ = MetadataStripper.strip_docx_metadata(raw_bytes)
                        cleaned_summary.append(f"{fn}: DOCX XML metadata scrubbed")
                    elif fn.lower().endswith(".svg"):
                        text_str = raw_bytes.decode("utf-8", errors="ignore")
                        clean_svg, _ = MetadataStripper.strip_svg_metadata(text_str)
                        cleaned_bytes = clean_svg.encode("utf-8")
                        cleaned_summary.append(f"{fn}: SVG metadata stripped")
                    elif fn.lower().endswith(".html") or fn.lower().endswith(".htm"):
                        text_str = raw_bytes.decode("utf-8", errors="ignore")
                        clean_html, _ = MetadataStripper.strip_html_metadata(text_str)
                        cleaned_bytes = clean_html.encode("utf-8")
                        cleaned_summary.append(f"{fn}: HTML generator metadata stripped")
                    else:
                        text_str = raw_bytes.decode("utf-8", errors="ignore")
                        clean_md, _ = MetadataStripper.strip_markdown_frontmatter(text_str)
                        cleaned_bytes = clean_md.encode("utf-8")
                        cleaned_summary.append(f"{fn}: Markdown frontmatter stripped")

                zout.writestr(item.filename, cleaned_bytes)
                files_processed += 1

        out_buf.seek(0)
        return out_buf.getvalue(), {
            "files_processed": files_processed,
            "summary_items": cleaned_summary
        }
