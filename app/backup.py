from __future__ import annotations
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from .db import AppPaths


def create_backup(paths: AppPaths) -> Path:
    """Create a consistent SQLite snapshot plus archived documents."""
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    staging = paths.backups / f"backup_{stamp}"
    staging.mkdir(parents=True, exist_ok=False)

    snapshot = staging / paths.database.name
    if paths.database.exists():
        source = sqlite3.connect(paths.database)
        target = sqlite3.connect(snapshot)
        try:
            source.backup(target)
        finally:
            target.close(); source.close()

    if paths.documents.exists():
        shutil.copytree(paths.documents, staging / "documents", dirs_exist_ok=True)

    archive = shutil.make_archive(str(staging), 'zip', staging)
    shutil.rmtree(staging, ignore_errors=True)
    return Path(archive)
