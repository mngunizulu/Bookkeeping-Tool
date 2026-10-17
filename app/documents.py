from __future__ import annotations

import hashlib
import mimetypes
import shutil
from datetime import datetime
from pathlib import Path

from .db import Database, AppPaths


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def archive_document(db: Database, paths: AppPaths, source: Path, document_type: str = "receipt") -> int:
    source = Path(source)
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(source)
    digest = sha256_file(source)
    day = datetime.now()
    folder = paths.documents / f"{day.year:04d}" / f"{day.month:02d}"
    folder.mkdir(parents=True, exist_ok=True)
    suffix = source.suffix.lower()
    safe_stem = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in source.stem)[:60] or "document"
    target = folder / f"{day.strftime('%Y%m%d_%H%M%S')}_{digest[:12]}_{safe_stem}{suffix}"
    if not target.exists():
        shutil.copy2(source, target)
    mime = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
    return db.add_document(
        original_name=source.name,
        stored_path=str(target),
        sha256=digest,
        mime_type=mime,
        file_size=target.stat().st_size,
        document_type=document_type,
    )
