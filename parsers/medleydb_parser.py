#!/usr/bin/env python
"""
Translates the MedleyDB Pitch and Melody Annotations to a set of JAMS files.

The original data is found online at the following URL:
    http://marl.smusic.nyu.edu/medleydb


Example:
./isohpnics_parser.py ~/Chord-Annotations -o ~/datasets/MARLChords/

"""

__author__ = "Rachel M. Bittner"
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


def fill_file_metadata(jam, yaml_file):
    """Fills the song-level metadata into the JAMS jam."""
    artist = yaml_file.split("/")[-3] if "uspop" in yaml_file else 'RWC-Pop'
    jam.file_metadata.artist = artist
    jam.file_metadata.title = os.path.basename(yaml_file).replace(".lab", "")


def fill_annotation_metadata(annot):
    """Fills the annotation metadata."""
    annot.annotation_metadata.corpus = "MARL-Chords"
    annot.annotation_metadata.version = "1.0"
    annot.annotation_metadata.annotation_tools = "Sonic Visualizer"
    annot.annotation_metadata.annotation_rules = ""  # TODO
    annot.annotation_metadata.validation_and_reliability = "TODO"  # TODO
    annot.annotation_metadata.origin = "MARL@NYU"
    annot.annotation_metadata.curator = dict(name="Tae Min Cho",
                                             email='tmc323@nyu.edu')
    annot.annotation_metadata.annotator = {}


def create_JAMS(lab_file, out_file):
    """Creates a JAMS file given the Isophonics lab file."""

    # New JAMS and annotation
    jam = pyjams.JAMS()

    # Global file metadata
    fill_file_metadata(jam, lab_file)

    # Create Chord annotation
    starts, ends, labels = pyjams.util.loadlab(lab_file, 3)
    chord_annot = jam.chord.create_annotation()
    pyjams.util.fill_range_annotation_data(starts, ends, labels, chord_annot)
    fill_annotation_metadata(chord_annot)
    jam.file_metadata.duration = ends[-1]

    # Save JAMS
    with open(out_file, "w") as f:
        json.dump(jam, f, indent=2)


def load_textlist(filename):
    with open(filename, 'r') as fp:
        filelist = [line.strip("\n") for line in fp]

    return filelist


def expand_filepaths(base_dir, rel_paths):
    return [os.path.join(base_dir, rp.strip("./")) for rp in rel_paths]


def create_output_dir(filename):
    # Check if output folder and create it if needed:
    out_dir = os.path.split(filename)[0]
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)


def process(in_dir, out_dir):
    """Converts the original chord labfiles into the JAMS format, and saves
    them in the out_dir folder."""

    # Collect all chord labfiles.
    lab_files = list()
    for dset in RWC_MANIFEST, USPOP_MANIFEST:
        lab_files += expand_filepaths(
            in_dir, load_textlist(os.path.join(in_dir, dset)))

    for lab_file in lab_files:
        jams_file = lab_file.replace(in_dir, out_dir).replace('.lab', '.jams')
        create_output_dir(jams_file)
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
