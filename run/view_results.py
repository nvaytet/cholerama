# SPDX-License-Identifier: BSD-3-Clause
import argparse

from cholerama import load, plot


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, default=None, nargs="?")
    return parser.parse_args()


def main():
    args = parse_args()
    plot(**load(args.file))


if __name__ == "__main__":
    main()
