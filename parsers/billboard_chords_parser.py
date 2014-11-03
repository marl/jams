#!/usr/bin/env python
"""Translates Billboard Chord Annotations to a set of JAMS files.

The original data is found online at the following URL:
    http://ddmal.music.mcgill.ca/billboard

Specifically, this parser converts the "MIREX-style" lab files, provided on the
dataset's homepage. To parse the entire dataset, you simply need to provide the
path to the unarchived folder downloaded from this site.

Keep in mind that the directory structure looks like the following:

    ~/McGill-Billboard/
        0003/
            full.lab
        0004/
            full.lab
        0006/
            full.lab
        ...


Additionally, providing the CSV file will backfill the appropriate information
in the `file_metadata` field.

Example:
./billboard_chords_parser.py \
~/McGill-Billboard \
-o ~/datasets/McGill-Billboard \
csv_index=~/billboard-2.0-index.csv

"""

__author__ = "E. J. Humphrey"
__copyright__ = "Copyright 2014, Music and Audio Research Lab (MARL)"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "ejhumphrey@nyu.edu"

import argparse
import json
import logging
import os
import sys
import time
import csv

sys.path.append("..")
import pyjams


def read_index(index_file):
    index = dict()
    reader = csv.reader(open(index_file))
    fields = reader.next()
    for row in reader:
        key = "%04d" % int(row[0])
        index[key] = dict([(k, v) for k, v in zip(fields, row)])

    return index


def fill_file_metadata(jam, index_data):
    """Fills the global metada into the JAMS jam."""
    jam.file_metadata.artist = index_data.pop('artist')
    jam.file_metadata.title = index_data.pop('title')
    jam.sandbox.update(**index_data)


def fill_annotation_metadata(annot):
    """Fills the annotation metadata."""
    annot.annotation_metadata.corpus = "Billboard-Chords"
    annot.annotation_metadata.version = "2.0.1"
    annot.annotation_metadata.data_source = "Graduate music students"
    annot.annotation_metadata.curator = pyjams.Curator(
        name="Ashley Bourgoyne", email='john.ashley.burgoyne@mail.mcgill.ca')
    annot.annotation_metadata.annotator = {}
    annot.sandbox = dict(
        ref_url="http://ddmal.music.mcgill.ca/billboard",
        citation="""@inproceedings{Burgoyne2011,
    author = {John Ashley Burgoyne and Jonathan Wild and Ichiro Fujinaga},
    booktitle = {Proceedings of the 12th International Society for Music Information Retrieval Conference},
    month = {October},
    title = {An Expert Ground Truth Set for Audio Chord Recognition and Music Analysis},
    pages = {633–638},
    volume = {12},
    year = {2011}}
    """)


def create_JAMS(lab_file, out_file, index_data=None):
    """Creates a JAMS file given the Isophonics lab file."""
    jam = pyjams.JAMS()

    # Global file metadata
    if index_data:
        fill_file_metadata(jam, index_data)

    # Create Chord annotation
    start_times, end_times, chord_labels = pyjams.util.read_lab(lab_file, 3)
    chord_annot = jam.chord.create_annotation()
    pyjams.util.fill_range_annotation_data(
        start_times, end_times, chord_labels, chord_annot)
    fill_annotation_metadata(chord_annot)
    jam.file_metadata.duration = end_times[-1]

    # Save JAMS
    with open(out_file, "w") as fp:
        json.dump(jam, fp, indent=2)


def process(in_dir, out_dir, index_file=None):
    """Converts the original chord labfiles into the JAMS format, and saves
    them in the out_dir folder."""

    index = dict() if index_file is None else read_index(index_file)
    pyjams.util.smkdirs(out_dir)
    for lab_file in pyjams.util.find_with_extension(in_dir, "lab"):
        key = lab_file.split("/")[-2]
        jams_file = os.path.join(out_dir, "%s.jams" % key)
        create_JAMS(lab_file, jams_file, index.get(key, None))


def main():
    """Main function to convert the dataset into JAMS."""
    parser = argparse.ArgumentParser(
        description="Converts the MARL-Chords dataset to the JAMS format",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("in_dir",
                        action="store",
                        help="Top-level Billboard folder")
    parser.add_argument("-o",
                        action="store",
                        dest="out_dir",
                        default="outJAMS",
                        help="Output JAMS folder")
    parser.add_argument("--index_file",
                        action="store",
                        dest="index_file",
                        default="",
                        help="Path to the provided CSV track index.")
    args = parser.parse_args()
    start_time = time.time()

    # Setup the logger
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)

    # Run the parser
    process(args.in_dir, args.out_dir, args.index_file)

    # Done!
    logging.info("Done! Took %.2f seconds.", time.time() - start_time)

if __name__ == '__main__':
    main()
