"""
Content Type Auto-Detector Engine
Identifies whether input is Text, Image, Audio, Video, or Container (PDF, DOCX, SVG, HTML) from byte headers or text patterns.
"""
import io
from PIL import Image

class ContentTypeDetector:
    @staticmethod
    def detect_file_type(file_bytes: bytes, filename: str = "") -> str:
        """Determines media modality: 'text' | 'image' | 'audio' | 'video' | 'container'"""
        fn_lower = filename.lower()
        
        # Extension heuristics
        if any(fn_lower.endswith(ext) for ext in ['.pdf', '.docx', '.svg', '.html', '.htm', '.odt']):
            return 'container'
        if any(fn_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif']):
            return 'image'
        if any(fn_lower.endswith(ext) for ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg']):
            return 'audio'
        if any(fn_lower.endswith(ext) for ext in ['.mp4', '.webm', '.avi', '.mov', '.mkv']):
            return 'video'
        if any(fn_lower.endswith(ext) for ext in ['.txt', '.md', '.json', '.csv']):
            return 'text'

        # Magic byte headers
        if file_bytes.startswith(b'%PDF'):
            return 'container'
        if file_bytes.startswith(b'PK\x03\x04'):  # Zip archive (e.g. DOCX)
            return 'container'
        if file_bytes.startswith(b'\xff\xd8\xff') or file_bytes.startswith(b'\x89PNG\r\n\x1a\n') or (file_bytes.startswith(b'RIFF') and b'WEBP' in file_bytes[:16]):
            return 'image'
        if file_bytes.startswith(b'ID3') or file_bytes.startswith(b'\xff\xfb') or (file_bytes.startswith(b'RIFF') and b'WAVE' in file_bytes[:16]):
            return 'audio'
        if file_bytes.startswith(b'\x00\x00\x00') and (b'ftyp' in file_bytes[:20] or b'moov' in file_bytes[:50]):
            return 'video'

        # Text UTF-8 validation fallback
        try:
            file_bytes.decode('utf-8')
            return 'text'
        except Exception:
            return 'image' # default fallback

