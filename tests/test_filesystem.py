from __future__ import annotations

from pathlib import Path

import pytest

from northtone.core.filesystem import FileSystem, FileSystemError


def test_list_dir_sorts_directories_first(tmp_path: Path) -> None:
    (tmp_path / "b_dir").mkdir()
    (tmp_path / "a_file.txt").write_text("abc", encoding="utf-8")
    (tmp_path / "a_dir").mkdir()

    fs = FileSystem()
    entries = fs.list_dir(tmp_path)
    names = [entry.name for entry in entries]

    assert names == ["a_dir", "b_dir", "a_file.txt"]


def test_list_dir_raises_for_missing_path(tmp_path: Path) -> None:
    fs = FileSystem()
    missing = tmp_path / "does-not-exist"

    with pytest.raises(FileSystemError):
        fs.list_dir(missing)


def test_copy_file(tmp_path: Path) -> None:
    fs = FileSystem()
    src = tmp_path / "source.txt"
    dst = tmp_path / "target.txt"
    src.write_text("hello", encoding="utf-8")

    fs.copy(src, dst)

    assert dst.read_text(encoding="utf-8") == "hello"


def test_copy_directory(tmp_path: Path) -> None:
    fs = FileSystem()
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "file.txt").write_text("x", encoding="utf-8")
    dst_dir = tmp_path / "dst"

    fs.copy(src_dir, dst_dir)

    assert (dst_dir / "file.txt").read_text(encoding="utf-8") == "x"


def test_copy_refuses_existing_destination_without_overwrite(tmp_path: Path) -> None:
    fs = FileSystem()
    src = tmp_path / "source.txt"
    dst = tmp_path / "target.txt"
    src.write_text("new", encoding="utf-8")
    dst.write_text("old", encoding="utf-8")

    with pytest.raises(FileSystemError):
        fs.copy(src, dst)

    assert dst.read_text(encoding="utf-8") == "old"


def test_copy_overwrites_file_when_requested(tmp_path: Path) -> None:
    fs = FileSystem()
    src = tmp_path / "source.txt"
    dst = tmp_path / "target.txt"
    src.write_text("new", encoding="utf-8")
    dst.write_text("old", encoding="utf-8")

    fs.copy(src, dst, overwrite=True)

    assert dst.read_text(encoding="utf-8") == "new"


def test_copy_refuses_directory_into_itself(tmp_path: Path) -> None:
    fs = FileSystem()
    src_dir = tmp_path / "src"
    nested_dst = src_dir / "nested-copy"
    src_dir.mkdir()

    with pytest.raises(FileSystemError):
        fs.copy(src_dir, nested_dst)


def test_move_rename(tmp_path: Path) -> None:
    fs = FileSystem()
    src = tmp_path / "name.txt"
    src.write_text("ok", encoding="utf-8")
    dst = tmp_path / "renamed.txt"

    fs.move(src, dst)

    assert not src.exists()
    assert dst.exists()


def test_move_refuses_existing_destination_without_overwrite(tmp_path: Path) -> None:
    fs = FileSystem()
    src = tmp_path / "source.txt"
    dst = tmp_path / "target.txt"
    src.write_text("new", encoding="utf-8")
    dst.write_text("old", encoding="utf-8")

    with pytest.raises(FileSystemError):
        fs.move(src, dst)

    assert src.exists()
    assert dst.read_text(encoding="utf-8") == "old"


def test_move_overwrites_file_when_requested(tmp_path: Path) -> None:
    fs = FileSystem()
    src = tmp_path / "source.txt"
    dst = tmp_path / "target.txt"
    src.write_text("new", encoding="utf-8")
    dst.write_text("old", encoding="utf-8")

    fs.move(src, dst, overwrite=True)

    assert not src.exists()
    assert dst.read_text(encoding="utf-8") == "new"


def test_move_refuses_directory_into_itself(tmp_path: Path) -> None:
    fs = FileSystem()
    src_dir = tmp_path / "src"
    nested_dst = src_dir / "nested-move"
    src_dir.mkdir()

    with pytest.raises(FileSystemError):
        fs.move(src_dir, nested_dst)

    assert src_dir.exists()


def test_delete_file_and_directory(tmp_path: Path) -> None:
    fs = FileSystem()
    file_path = tmp_path / "remove.txt"
    file_path.write_text("remove", encoding="utf-8")
    dir_path = tmp_path / "remove-dir"
    dir_path.mkdir()
    (dir_path / "nested.txt").write_text("nested", encoding="utf-8")

    fs.delete(file_path)
    fs.delete(dir_path)

    assert not file_path.exists()
    assert not dir_path.exists()


def test_mkdir_creates_directory(tmp_path: Path) -> None:
    fs = FileSystem()
    target = tmp_path / "new-dir"

    fs.mkdir(target)

    assert target.exists()
    assert target.is_dir()
