"""Filesystem business logic for NorthTone Commander."""

from __future__ import annotations

import os
import shutil
import stat
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


class FileSystemError(RuntimeError):
    """Raised when a filesystem operation fails."""


@dataclass
class FileEntry:
    path: Path
    name: str
    is_dir: bool
    is_file: bool
    is_symlink: bool
    is_executable: bool
    size: int
    modified: datetime


class FileSystem:
    """Performs all filesystem operations without UI dependencies."""

    def list_dir(self, path: Path) -> list[FileEntry]:
        target = path.expanduser()
        if not target.exists():
            raise FileSystemError(f"Cannot open directory: path does not exist ({target})")
        if not target.is_dir():
            raise FileSystemError(f"Cannot open directory: not a directory ({target})")

        try:
            children = list(target.iterdir())
        except OSError as exc:
            raise FileSystemError(self._error_message("Cannot open directory", exc)) from exc

        entries: list[FileEntry] = []
        for child in children:
            try:
                entries.append(self._to_entry(child))
            except OSError:
                continue

        entries.sort(key=lambda entry: (not entry.is_dir, entry.name.lower()))
        return entries

    def copy(self, src: Path, dst: Path, *, overwrite: bool = False) -> None:
        source = src.expanduser()
        destination = dst.expanduser()
        self._ensure_source_exists("Copy failed", source)
        self._ensure_destination_allowed("Copy failed", source, destination, overwrite=overwrite)

        try:
            if source.is_dir() and not source.is_symlink():
                self._ensure_not_nested("Copy failed", source, destination)
                if overwrite:
                    self._remove_existing(destination)
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
        except OSError as exc:
            raise FileSystemError(self._error_message("Copy failed", exc)) from exc

    def move(self, src: Path, dst: Path, *, overwrite: bool = False) -> None:
        source = src.expanduser()
        destination = dst.expanduser()
        self._ensure_source_exists("Move failed", source)
        self._ensure_destination_allowed("Move failed", source, destination, overwrite=overwrite)

        try:
            if source.is_dir() and not source.is_symlink():
                self._ensure_not_nested("Move failed", source, destination)
            if overwrite:
                self._remove_existing(destination)
            shutil.move(str(source), str(destination))
        except OSError as exc:
            raise FileSystemError(self._error_message("Move failed", exc)) from exc

    def delete(self, path: Path) -> None:
        target = path.expanduser()
        if not target.exists() and not target.is_symlink():
            raise FileSystemError(f"Delete failed: path does not exist ({target})")

        try:
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
        except OSError as exc:
            raise FileSystemError(self._error_message("Delete failed", exc)) from exc

    def mkdir(self, path: Path) -> None:
        target = path.expanduser()
        try:
            target.mkdir(parents=False, exist_ok=False)
        except OSError as exc:
            raise FileSystemError(self._error_message("Create directory failed", exc)) from exc

    @staticmethod
    def path_exists(path: Path) -> bool:
        """Return True for existing paths and broken symlinks."""
        return os.path.lexists(path.expanduser())

    def _to_entry(self, path: Path) -> FileEntry:
        info = path.lstat()
        is_symlink = path.is_symlink()
        is_dir = path.is_dir()
        is_file = path.is_file()
        is_executable = bool(info.st_mode & stat.S_IXUSR) and is_file
        size = info.st_size if is_file else 0
        modified = datetime.fromtimestamp(info.st_mtime)

        return FileEntry(
            path=path,
            name=path.name,
            is_dir=is_dir,
            is_file=is_file,
            is_symlink=is_symlink,
            is_executable=is_executable,
            size=size,
            modified=modified,
        )

    @staticmethod
    def _error_message(prefix: str, exc: OSError) -> str:
        details = exc.strerror or str(exc)
        return f"{prefix}: {details}"

    def _ensure_source_exists(self, prefix: str, source: Path) -> None:
        if not self.path_exists(source):
            raise FileSystemError(f"{prefix}: source does not exist ({source})")

    def _ensure_destination_allowed(
        self,
        prefix: str,
        source: Path,
        destination: Path,
        *,
        overwrite: bool,
    ) -> None:
        parent = destination.parent
        if not parent.exists():
            raise FileSystemError(f"{prefix}: destination directory does not exist ({parent})")
        if not parent.is_dir():
            raise FileSystemError(f"{prefix}: destination parent is not a directory ({parent})")

        same_path = self._same_path(source, destination)
        if same_path:
            raise FileSystemError(f"{prefix}: source and destination are the same ({source})")

        if self.path_exists(destination) and not overwrite:
            raise FileSystemError(f"{prefix}: destination already exists ({destination})")

    def _ensure_not_nested(self, prefix: str, source: Path, destination: Path) -> None:
        source_resolved = source.resolve()
        destination_resolved = destination.resolve(strict=False)
        if destination_resolved.is_relative_to(source_resolved):
            raise FileSystemError(f"{prefix}: destination is inside the source directory ({destination})")

    def _remove_existing(self, path: Path) -> None:
        if not self.path_exists(path):
            return
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()

    @staticmethod
    def _same_path(left: Path, right: Path) -> bool:
        try:
            return left.samefile(right)
        except OSError:
            return left.resolve(strict=False) == right.resolve(strict=False)
