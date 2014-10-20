#!/usr/bin/env python
"""
Translates the MedleyDB Melody and Instrument Activation annotations to a set 
of JAMS files.

The original data is found online at the following URL:
    http://marl.smusic.nyu.edu/medleydb


Example:
./medleydb_parser.py MedleyDB/ [-o MedleyDB_JAMS/]

"""

__author__ = "Rachel M. Bittner"
__copyright__ = "Copyright 2014, Music and Audio Research Lab (MARL)"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "rachel.bittner@nyu.edu"

import argparse
import json
import logging
import os
import sys
import time
import yaml

sys.path.append("..")
import pyjams
import pyjams.util as U


MEL1 = "The f0 curve of predominant melodic line drawn from a single source"
MEL2 = "The f0 curve of predominant melodic line drawn from multiple sources"
MEL3 = "The f0 curves of all melodic lines drawn from multiple sources"
MELODY_DEFS = {1: MEL1, 2: MEL2, 3: MEL3}


def fill_file_metadata(jam, artist, title):
    """Fills the song-level metadata into the JAMS jam."""
    
    jam.file_metadata.artist = artist
    jam.file_metadata.title = title


def fill_genre_annotation_metadata(annot):
    """Fills the annotation metadata."""
    annot.annotation_metadata.corpus = "MedleyDB"
    annot.annotation_metadata.version = "1.0"
    annot.annotation_metadata.annotation_tools = ""
    annot.annotation_metadata.annotation_rules = ""
    annot.annotation_metadata.validation = "None"
    annot.annotation_metadata.data_source = "Manual Annotation"
    annot.annotation_metadata.curator = pyjams.Curator(name="Rachel Bittner",
                                                       email='rachel.bittner@nyu.edu')
    annot.annotation_metadata.annotator = {}


def fill_melody_annotation_metadata(annot, mel_type):
    """Fills the annotation metadata."""
    annot.annotation_metadata.corpus = "MedleyDB"
    annot.annotation_metadata.version = "1.0"
    annot.annotation_metadata.annotation_tools = "Tony"
    annot.annotation_metadata.annotation_rules = MELODY_DEFS[mel_type]
    annot.annotation_metadata.validation = "Manual Validation"
    annot.annotation_metadata.data_source = "Manual Annotation"
    annot.annotation_metadata.curator = pyjams.Curator(name="Rachel Bittner",
                                                       email='rachel.bittner@nyu.edu')
    annot.annotation_metadata.annotator = {}


def fill_instid_annotation_metadata(annot):
    """Fills the annotation metadata."""
    annot.annotation_metadata.corpus = "MedleyDB"
    annot.annotation_metadata.version = "1.0"
    annot.annotation_metadata.annotation_tools = ""
    annot.annotation_metadata.annotation_rules = ""
    annot.annotation_metadata.validation = "None"
    annot.annotation_metadata.data_source = "Automatic Annotation"
    annot.annotation_metadata.curator = pyjams.Curator(name="Juan P. Bello",
                                                       email='jpbello@nyu.edu')
    annot.annotation_metadata.annotator = {}


def fill_melody_annotation(annot_fpath, melody_annot, mel_type):
    """Fill a melody annotation with data from annot_fpath."""
    times, values = U.read_lab(annot_fpath, 2, delimiter=",")
    U.fill_timeseries_annotation_data(times, values, None, melody_annot)
    fill_melody_annotation_metadata(melody_annot, mel_type)


def fill_instid_annotation(annot_fpath, instid_annot):
    """Fill an instrument id annotation with data from annot_fpath."""
    start_times, end_times, inst_labels = U.read_lab(annot_fpath, 3, 
                                                     delimiter=",", header=True)
    U.fill_range_annotation_data(start_times, end_times, inst_labels, 
                                 instid_annot)
    fill_instid_annotation_metadata(instid_annot)


def create_JAMS(dataset_dir, trackid, out_file):
    """Creates a JAMS file given the Isophonics lab file."""

    metadata_file = os.path.join(dataset_dir, 'Audio', trackid, 
                                 '%s_METADATA.yaml' % trackid)

    with open(metadata_file, 'r') as f_in:
        metadata = yaml.load(f_in)


    # New JAMS and annotation
    jam = pyjams.JAMS()

    # Global file metadata
    fill_file_metadata(jam, metadata['artist'], metadata['title'])

    # Create Genre Annotation
    genre_annot = jam.genre.create_annotation()
    U.fill_observation_annotation_data([metadata['genre']], [1], [""], 
                                       genre_annot)
    fill_genre_annotation_metadata(genre_annot)

    # Create Melody Annotations
    melody_path = os.path.join(dataset_dir, 'Annotations', 'Melody_Annotations')
    
    melody1_fpath = os.path.join(melody_path, 'MELODY1', 
                                 "%s_MELODY1.csv" % trackid)
    if os.path.exists(melody1_fpath):
        melody1_annot = jam.melody.create_annotation()
        fill_melody_annotation(melody1_fpath, melody1_annot, 1)

    melody2_fpath = os.path.join(melody_path, 'MELODY2', 
                                 "%s_MELODY2.csv" % trackid)
    if os.path.exists(melody2_fpath):
        melody2_annot = jam.melody.create_annotation()
        fill_melody_annotation(melody2_fpath, melody2_annot, 2)

    # Create SourceID Annotation
    instid_fpath = os.path.join(dataset_dir, 'Annotations', 
                                'Instrument_Activations', 'SOURCEID',
                                "%s_SOURCEID.lab" % trackid)
    if os.path.exists(instid_fpath):
        instid_annot = jam.source.create_annotation()
        fill_instid_annotation(instid_fpath, instid_annot)

    # jam.file_metadata.duration = end_times[-1]

    # Save JAMS
    with open(out_file, "w") as fp:
        json.dump(jam, fp, indent=2)


def process(in_dir, out_dir):
    """Converts MedleyDB Annotations into JAMS format, and saves
    them in the out_dir folder."""

    # Collect all trackid's.
    yaml_files = U.find_with_extension(os.path.join(in_dir, 'Audio'), 'yaml')
    trackids = [U.filebase(y).replace("_METADATA", "") for y in yaml_files]

    U.smkdirs(out_dir)

    for trackid in trackids:
        jams_file = os.path.join(out_dir, "%s.jams" % trackid)
        #Create a JAMS file for this track
        create_JAMS(in_dir, trackid, jams_file)


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
