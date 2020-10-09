#!/usr/bin/env python
"""Tests for `dlink` package."""
from dlink.core import get_basenames
from pathlib import Path

import pytest

from dlink import core


def test_symlink(tmp_path):
    d = tmp_path
    d.mkdir(exist_ok=True)
    dest = d / "any_file.txt"
    dest.write_text("Probably not necessary")
    # Start with a path object. Then parameterize this?
    src = tmp_path / "link"
    core.symlink(src, dest)
    assert Path.is_symlink(src)
    assert Path.is_file(dest)


def test_generate_dest(tmp_path):
    # At the risk of this not being super clear.
    # 1. Make a directory and a bunch of files.
    base = tmp_path / "base"
    base.mkdir()
    for i in range(5):
        # This is kinda sloppy because / makes a new directory and I'm genuinely
        # unsure of what the clean way to concatenate strings and Paths together
        (base / (str(i) + ".txt")).write_text("Foo")
    ret = core.generate_dest(base)
    for i in range(5):
        file = base / (str(i) + ".txt")
        assert file == ret[i]


if __name__ == "__main__":
    pytest.main()
