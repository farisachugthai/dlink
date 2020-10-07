#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Main module.

Console script for dlink.
"""
import argparse
import logging
import sys
import traceback
from pathlib import Path
from typing import Union

# from . import __version__


class UsageError(Exception):
    """Symlinking error typically from Windows."""

    def __call__(self, tb=None):
        if tb:
            return "{}".format(traceback.format_tb(tb))


def _parse_arguments():
    """Parse arguments given by the user.

    Returns
    -------
    args : :class:`argparse.NameSpace()`
        Arguments provided by the user and handled by argparse.

    """
    parser = argparse.ArgumentParser(
        prog="Directory Linker 2.0",
        description="Iterate over a `dest` folder"
        " and create symlinks in directory "
        "`source`. If `source` is not provided use"
        " current working directory.",
    )

    parser.add_argument(
        "destination",
        metavar="destination",
        nargs="?",
        type=Path,
        help="Files to symlink to.",
    )

    parser.add_argument(
        "-s",
        "--source_directory",
        metavar="SOURCE_DIRECTORY",
        dest="source",
        nargs="?",
        default=Path().cwd(),
        help="Where to create the symlinks. Defaults to the cwd.",
    )

    parser.add_argument(
        "-g",
        "--glob-pattern",
        metavar="GLOB_PATTERN",
        default=None,
        nargs=1,
        help="Filter files in the destination dir with a glob pattern."
        " This ensures that only files that match GLOB_PATTERN in `dst`"
        " are symlinked in `src`.",
    )

    # so apparently without the metavar argument, args won't show their var
    # name in the help message?
    parser.add_argument(
        "-R",
        "--recursive",
        action="store_const",
        # nargs='?',
        default=False,
        const=True,
        metavar="RECURSIVE",  # and it causes an error too!
        help="Whether to recursively symlink the files in"
        " child directories below the destination folder as well.",
    )

    parser.add_argument(
        "-l",
        "--log",
        action="store_false",
        help="Where to write log records to. Defaults to stdout.",
    )

    parser.add_argument(
        "-ll",
        "--log-level",
        dest="log_level",
        choices=[10, 20, 30, 40, 50],
        type=int,
        help="Log level. If logging is specified with '-l', defaults to INFO.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_false",
        help="Shorthand to enable verbose logging and increase level to `debug`.",
    )

    # parser.add_argument("--version", action="version", version=__version__)

    if len(sys.argv[1:]) == 0:
        parser.print_help()
        # This is actually annoying
        # raise argparse.ArgumentError(None, "Args not provided.")
        # sys.exit()

    args = parser.parse_args()

    # handle a few of our args
    if args.log_level is None:
        # no LOG_LEVEL specified but -l was specified
        if args.log is not None:
            LOG_LEVEL = logging.WARNING
        else:
            # Don't log
            LOG_LEVEL = 99
    else:
        LOG_LEVEL = args.log_level

    logging.basicConfig(level=LOG_LEVEL)

    return args


def generate_dest(dest, glob_pattern=None):
    """Return a generator for all the files in the destination directory.

    Parameters
    ----------
    dest : str
        Directory to find files in.
    glob_pattern : str, optional

    Yields
    ------
    `pathlib.Path`
        File objects in dir.

    """
    if not hasattr(dest, "iterdir"):
        dest = Path(dest)
    if not dest.exists():
        try:
            dest.mkdir()
        except PermissionError:
            logging.error(
                "Permissions issue in source directory."
                "Can't create needed directories for recursive symlinks."
            )
        except OSError:
            logging.error(f"{dest}", exc_info=1)
    if glob_pattern is None:
        glob_pattern = '*'
    ret = [i for i in dest.glob(glob_pattern)]
    return ret


def get_basenames(directory: Path, glob_pattern: str = None) -> Union[list, Path]:
    """Get the basenames of all the files in a directory."""
    if not hasattr(directory, "iterdir"):
        directory = Path(directory)
    if glob_pattern is None:
        glob_pattern = '*'
    ret = [i for i in directory.glob(glob_pattern)]
    return ret


def dlink(destination_dir, source_dir=None, is_recursive=False, glob_pattern=None):
    """Symlink user provided files.

    Parameters
    ----------
    destination_dir : str
        Directory where symlinks point to.
    source_dir : str, optional
        Directory where symlinks are created.
    is_recursive : bool, optional
        Whether to recursively symlink directories beneath the
        `destination_dir`. Defaults to False.
    glob_pattern : str
        Only symlink files that match a certain pattern.

    """
    if source_dir is None:
        source_dir = Path.cwd()
    base_destination_files = sorted(get_basenames(destination_dir, glob_pattern))

    if not hasattr(destination_dir, "iterdir"):
        destination_dir = Path(destination_dir)

    full_destination_files = sorted([j for j in generate_dest(destination_dir, glob_pattern)])

    full_source_files = sorted(
        Path(source_dir).joinpath(i) for i in base_destination_files
    )

    for idx, src_file in enumerate(full_source_files):
        logging.debug("\ni is {0!s}".format(src_file))
        # most useful but way too long
        # logging.info("\nfull_destination_files is {!s}".format(full_destination_files))
        logging.debug("\nfull_source_files is {!s}".format(full_source_files))
        logging.debug("\nsource_dir is {}".format(source_dir))
        logging.debug("\nbase_destination_files: {!r}".format(base_destination_files))
        logging.debug("idx: {}\tsrc_file: {}\t".format(idx, src_file))
        if full_destination_files[idx].is_dir():
            src_dir = Path(src_file)
            if not src_dir.exists():
                src_dir.mkdir(0o755)

            # then call it recursively
            if src_file.is_dir():
                dlink(
                    destination_dir=src_file,
                    source_dir=source_dir.joinpath(src_file),
                    is_recursive=is_recursive,
                    glob_pattern=glob_pattern,
                )

        else:
            symlink(src_file, full_destination_files[idx])


def symlink(src, dest):
    """Execute the symlinking part of this."""
    try:
        src.symlink_to(dest)
    except FileExistsError:
        pass
    except OSError as e:
        # let's be a little more specific
        # except WindowsError: breaks linux
        if hasattr(e, "winerror"):
            raise PermissionError(
                "{}".format(e) + "Ensure that you are running this script as an admin"
                " when running on Windows!"
            )


def main():
    """Call :func:`_parse_arguments` and the :func:`dlink` function."""
    user_arguments = _parse_arguments()
    args = user_arguments.parse_args()

    if args.destination is None:
        raise UsageError("No destination given")
    # yeah we also need to resolve or else relative paths dont work
    dest = args.destination.expanduser().resolve()

    if not dest.is_dir():
        sys.exit("Provided target not a directory. Exiting.")

    src = args.source or Path().cwd

    try:
        glob_search = args.glob_pattern
    except AttributeError:
        glob_search = None

    try:
        recursive = args.recursive
    except AttributeError:
        recursive = False

    dlink(dest, source_dir=src, is_recursive=recursive, glob_pattern=glob_search)


if __name__ == "__main__":
    (main())
