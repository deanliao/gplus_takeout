#!/usr/bin/python

"""A tool to read photos directory, retrieve metadata and stores in db.
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
import csv
import json
import logging
import os

import path_util


def ParsePhotosImpl(base, files):
    result = []
    postfix = '.metadata.csv'
    photo_meta = []
    rest_files = []
    # Used for sanity check (prefix should be unique).
    prefix_set = set()
    for fn in files:
        pos = fn.rfind(postfix)
        if pos == -1:
            rest_files.append(fn)
            continue
        meta_fn = fn
        prefix = fn[:pos]
        if prefix in prefix_set:
            logging.warning('Prefix already exists: %s', prefix)
        else:
            prefix_set.add(prefix)
            photo_meta.append((meta_fn, prefix))

    # Used for exact match.
    rest_file_set = set(rest_files)

    for meta_fn, prefix in photo_meta:
        meta_path = os.path.join(base, meta_fn)
        photo_fn = prefix
        if prefix not in rest_file_set:
            # Prefix match each file.
            matched_files = []
            for f in rest_files:
                if f.find(prefix) == 0:
                    matched_files.append(f)
            if not matched_files:
                logging.warning(
                    'Unable to find corresponding photo %s for metadata %s',
                    prefix, meta_path)
                continue
            if len(matched_files) > 1:
                matched_files.sort(key=len)
                photo_fn = matched_files[0]
                logging.info(
                    'More than one corresponding photos %s for metadata %s. '
                    'Guess %s', matched_files, meta_path, photo_fn)
        meta_dict = ParseMetadataCsv(meta_path)
        photo_path = os.path.join(base, photo_fn)
        url = meta_dict['url']
        result.append((url, photo_path, meta_dict))

    return result


def ParsePhotos(base_dir, output_fn):
    """Parse G+ backup photos' metadata.
    """
    logging.info('Parse photos with metadata in %s', base_dir)
    dir_files = path_util.TraverseDir(base_dir)
    result = []
    for (subdir, files) in dir_files:
        # Sanity check
        if subdir.find(base_dir) != 0:
            logging.error('Subdir %s should begin with %s', subdir, base_dir)
            continue
        if not files:
            continue
        result.extend(ParsePhotosImpl(subdir, files))

    with open(output_fn, 'w') as json_fp:
        json.dump(result, json_fp)
    print 'Output %d photos into JSON db' % len(result)


def ParseMetadataCsv(filename):
    result = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            result.append(row)
    if len(result) != 1:
        logging.warning('Expect single row in metadata: %s, actual: %d',
                        filename, len(result))
        if not result:
            return None
    return result[0]


def main():
    parser = argparse.ArgumentParser(description='Parse photos')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show verbose messages')
    parser.add_argument(
        'photo_dir', metavar='photo_dir',
        help='Directories where photos and metadata resides')
    parser.add_argument(
        'output', metavar='output',
        help='Output JSON: [[URL, photo_filename, photo_metadata], ...]')

    args = parser.parse_args()
    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level)

    ParsePhotos(args.photo_dir, args.output)


if __name__ == '__main__':
    main()
