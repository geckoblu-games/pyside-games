#!/usr/bin/python3

import argparse
import os
import pathlib
import sys


class Sok2Py:

    def __init__(self):
        self.collection_name = None
        self.levels = []

    def run(self, inputfile, outfile):
        print("Input: ", inputfile.name)
        print("Output:", outfile.name)
        self._parse_inputfile(inputfile)
        # print(self.levels)
        self._write_module(outfile)

    def _parse_inputfile(self, inputfile):
        self.levels = []
        inputlines = inputfile.readlines()

        inlevel = False
        level = []
        for i, line in enumerate(inputlines):
            stripped_line = line.strip()

            # Comment
            if stripped_line.startswith('::'):
                continue

            # Collection name
            if stripped_line.startswith('Collection'):
                self.collection_name = stripped_line[len('Collection:'):].strip()
                print('')
                print("Collection:", self.collection_name)
                continue

            if not inlevel and '#' in stripped_line:
                inlevel = True
                title = inputlines[i - 2].strip()
                if title.startswith('; '):  # Microban
                    title = title[2:]
                title = title.replace("'", "\\'")
                # print(title)
                level.append(line.rstrip())
                continue

            if inlevel and stripped_line == '':
                inlevel = False
                self.levels.append((title, level))
                level = []
                continue

            if inlevel:
                level.append(line.rstrip())
                continue

        if len(level) > 0:
            self.levels.append((title, level))

    def _write_module(self, outfile):

        outfile.write('# pylint: disable=bad-continuation,too-many-lines\n')
        outfile.write('\n')
        outfile.write('def append_set(sets):\n')
        outfile.write(f"    sets['{self.collection_name}'] = _SET\n")
        outfile.write('\n')

        outfile.write('_SET = {}\n')

        for title, level in self.levels:
            outfile.write('\n')
            outfile.write(f"_SET['{title}'] = [\n")

            for line in level:
                outfile.write(f'\t"{line}",\n')

            outfile.write(f"]\n")


def main():
    if args.OUTPUT_FILE_OR_DIR.is_dir():
        basename = os.path.basename(args.INPUT_SOK_FILE.name)
        basename, __ = os.path.splitext(basename)
        basename = basename.lower()
        basename = basename.replace(' ', '_')
        modulename = os.path.join(args.OUTPUT_FILE_OR_DIR, f'{basename}.py')
    else:
        modulename = args.OUTPUT_FILE_OR_DIR

    outfile = open(modulename, 'w')

    sok2py = Sok2Py()
    sok2py.run(args.INPUT_SOK_FILE, outfile)


def parse_cmdline():
    parser = argparse.ArgumentParser()

    parser.add_argument('INPUT_SOK_FILE', type=argparse.FileType('r'),
                        help='Input SOK file to convert')
    parser.add_argument('OUTPUT_FILE_OR_DIR', type=pathlib.Path,
                        help='Ouptut python module (if a dir is passed, the module name is the input file name)') # pylint: disable=line-too-long

    return parser.parse_args()


if __name__ == '__main__':

    args = parse_cmdline()
    # print(args)

    sys.exit(main())
