#!/usr/bin/python

"""A tool to merge multiple directories into one.

It is useful if you have multiple directories with similiar subdirectory
structure, and you want to put files of the same subdirectory together.
"""

# Copyright (c) 2019 Dean Liao
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import logging
import os
import shutil
import sys


def TraverseDir(root_dir):
    """Returns all files under root_dir recursively.

    It returns a list of (subdir, list of files in the subdir).
    Noted that it skips empty subdirs.
    """
    result = []
    for dir_name, subdirs, files in os.walk(root_dir):
        if files:
            result.append((dir_name, files))
    return result


def MergeDir(from_dir, dest_dir):
    """Merges directory content recursively.

    It copies files from from_dir and its subdirs to dest_dir.
    If a file already exists, it is skipped.
    It also creates subdirs when needed.
    """
    logging.info('Merge directory from %s to %s', from_dir, dest_dir)
    dir_files = TraverseDir(from_dir)
    for (subdir, files) in dir_files:
        if subdir.find(from_dir) != 0:
            logging.error('Subdir %s should begin with %s', subdir, from_dir)
            continue
        # Replace subdir's root dir, which is from_dir, with dest_dir.
        target_dir = dest_dir + subdir[len(from_dir):]

        if not os.path.exists(target_dir):
            logging.info('Creating path %s for copying %d files from %s',
                         target_dir, len(files), subdir)
            os.makedirs(target_dir)

        if not os.path.isdir(target_dir):
            logging.error('Expect %s a directory, which is not', target_dir)
            continue

        logging.info('Copying %d files: %s => %s', len(files), subdir,
                     target_dir)
        for filename in files:
            source_file_path = os.path.join(subdir, filename)
            target_file_path = os.path.join(target_dir, filename)
            if os.path.exists(target_file_path):
                logging.warning('Skip copying %s to %s: file exists',
                                source_file_path, target_file_path)
                continue
            shutil.copy(source_file_path, target_file_path)


def main():
    parser = argparse.ArgumentParser(description='Merge directories')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show verbose messages')
    parser.add_argument(
        'dirs', metavar='dir', nargs='+',
        help='Directories to be merged. The last one is the target')
    args = parser.parse_args()
    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level)
    if len(args.dirs) < 2:
        logging.error('Must provide at least two directories')
        sys.exit(1)

    from_dirs = args.dirs[:-1]
    dest_dir = args.dirs[-1]
    for d in from_dirs:
        if not os.path.isdir(d):
            logging.error('Source directory does not exist: ', d)
            sys.exit(1)

    for from_dir in from_dirs:
        MergeDir(from_dir, dest_dir)


if __name__ == '__main__':
    main()
