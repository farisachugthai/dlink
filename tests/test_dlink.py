#!/usr/bin/env python
"""Tests for `dlink` package."""
import os
from argparse import Namespace
from pathlib import Path

import pytest

from dlink import core


@pytest.fixture
def populate(tmp_path):
    # At the risk of this not being super clear.
    # 1. Make a directory and a bunch of files.
    base = tmp_path / "base"
    base.mkdir()
    for i in range(5):
        # This is kinda sloppy because / makes a new directory and I'm genuinely
        # unsure of what the clean way to concatenate strings and Paths together
        (base / (str(i) + ".txt")).write_text("Foo")

    return base


@pytest.fixture
def args(tmp_path, populate):
    namespace = Namespace()
    namespace.destination = populate
    namespace.log = True
    namespace.log_level = 10
    namespace.recursive = False
    namespace.glob_pattern = ""
    namespace.source = tmp_path / "src"
    namespace.source.mkdir()
    return namespace


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


def test_generate_dest(populate):
    ret = core.generate_dest(populate)
    for i in range(5):
        file = populate / (str(i) + ".txt")
        assert file == ret[i]


def test_main(args):
    os.chdir(args.source)
    core.main(args)
    assert "0.txt" in os.listdir()


def test_logging(args, caplog):
    os.chdir(args.source)
    core.main(args)
    for record in caplog.records:
        assert record.levelname != "ERROR"


if __name__ == "__main__":
    pytest.main()
