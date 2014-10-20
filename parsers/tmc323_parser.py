#!/usr/bin/env python
"""Translates the MARL Chord Annotations to a set of JAMS files.

The original data is found online at the following URL:
    https://github.com/tmc323/Chord-Annotations

To parse the entire dataset, you simply need to provide the path to the
unarchived folder downloaded from GitHub.

Example:
./isohpnics_parser.py ~/Chord-Annotations -o ~/datasets/MARLChords/

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

sys.path.append("..")
import pyjams

RWC_MANIFEST = "RWC_Pop_Chords.txt"
USPOP_MANIFEST = "uspopLabels.txt"


def fill_file_metadata(jam, lab_file):
    """Fills the global metada into the JAMS jam."""
    artist = lab_file.split("/")[-3] if "uspop" in lab_file else 'RWC-Pop'
    jam.file_metadata.artist = artist
    jam.file_metadata.title = os.path.basename(lab_file).replace(".lab", "")


def fill_annotation_metadata(annot):
    """Fills the annotation metadata."""
    annot.annotation_metadata.corpus = "MARL-Chords"
    annot.annotation_metadata.version = "1.0"
    annot.annotation_metadata.annotation_tools = "Sonic Visualizer"
    annot.annotation_metadata.annotation_rules = ""
    annot.annotation_metadata.validation = "TODO"
    annot.annotation_metadata.data_source = "Undergraduate music students"
    annot.annotation_metadata.curator = pyjams.Curator(name="Tae Min Cho",
                                                       email='tmc323@nyu.edu')
    annot.annotation_metadata.annotator = {}


def create_JAMS(lab_file, out_file):
    """Creates a JAMS file given the Isophonics lab file."""

    # New JAMS and annotation
    jam = pyjams.JAMS()

    # Global file metadata
    fill_file_metadata(jam, lab_file)

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


def process(in_dir, out_dir):
    """Converts the original chord labfiles into the JAMS format, and saves
    them in the out_dir folder."""

    # Collect all chord labfiles.
    lab_files = list()
    for dset in RWC_MANIFEST, USPOP_MANIFEST:
        lab_files += pyjams.util.expand_filepaths(
            in_dir, pyjams.util.load_textlist(os.path.join(in_dir, dset)))

    for lab_file in lab_files:
        jams_file = os.path.join(
            out_dir, os.path.basename(lab_file).replace('.lab', '.jams'))
        pyjams.util.smkdirs(os.path.split(jams_file)[0])
        #Create a JAMS file for this track
        create_JAMS(lab_file, jams_file)


def main():
    """Main function to convert the dataset into JAMS."""
    parser = argparse.ArgumentParser(
        description="Converts the MARL-Chords dataset to the JAMS format",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("in_dir",
                        action="store",
                        help="Isophonics main folder")
    parser.add_argument("-o",
                        action="store",
                        dest="out_dir",
                        # TODO(ejhumphrey): This should be a config, no?
                        default="outJAMS",
                        help="Output JAMS folder")
    args = parser.parse_args()
    start_time = time.time()

    # Setup the logger
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)

    # Run the parser
    process(args.in_dir, args.out_dir)

    # Done!
    logging.info("Done! Took %.2f seconds.", time.time() - start_time)

if __name__ == '__main__':
    main()
