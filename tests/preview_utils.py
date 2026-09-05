"""Create self-contained HTML for offline previews and browser checks.

Production output remains normal static HTML with separate local assets.
Only preview files embed their CSS, scripts, and images.
"""
from __future__ import annotations
import base64
import mimetypes
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'


def inline_page(path: Path, base_prefix: str = '') -> str:
    text=path.read_text(encoding='utf-8')
    def local(url: str) -> Path:
        relative = urlparse(url).path
        if base_prefix and relative.startswith(base_prefix+'/'):
            relative=relative[len(base_prefix):]
        return SITE/relative.lstrip('/')
    def css(match: re.Match) -> str:
        return '<style>'+local(match[1]).read_text(encoding='utf-8')+'</style>'
    text=re.sub(r'<link rel="stylesheet" href="([^"]+)">',css,text)
    deferred=[]
    def script(match: re.Match) -> str:
        code=local(match[1]).read_text(encoding='utf-8')
        if match[2]:
            deferred.append(code)
            return ''
        return '<script>'+code+'</script>'
    text=re.sub(r'<script src="([^"]+)"( defer)?></script>',script,text)
    text=re.sub(r' srcset="[^"]+"','',text)
    def image(match: re.Match) -> str:
        file=local(match[1])
        mime=mimetypes.guess_type(file)[0] or 'application/octet-stream'
        return 'src="data:'+mime+';base64,'+base64.b64encode(file.read_bytes()).decode()+'"'
    text=re.sub(r'src="(/[^\"]+\.(?:webp|png|jpg|jpeg))"',image,text)
    text=re.sub(r'<link rel="icon"[^>]+>','',text)
    return text.replace('</body>',''.join('<script>'+code+'</script>' for code in deferred)+'</body>')
