"""Visualize a Piano"""
import argparse
import os
import sys
from typing import Sequence

from drawing.piano_drawing import draw_piano
from instruments.piano_instrument import generate_piano_keys


def _parse_arguments(argv: Sequence[str]):
    parser = argparse.ArgumentParser(description="Piano entry point")
    parser.add_argument("-v", "--visualize", action="store_true")
    parser.add_argument("-s", "--save-to-file", action="store_true")
    parser.add_argument(
        "-f",
        "--file-path",
        type=str,
        required=False,
        help="for saving",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str]):
    # pylint: disable=missing-function-docstring
    args = _parse_arguments(argv)
    piano_keys = generate_piano_keys()
    draw_piano(piano_keys, args.visualize, args.save_to_file, args.file_path)
    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))