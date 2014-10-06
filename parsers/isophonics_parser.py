#!/usr/bin/env python
"""
Converts an Isophonics dataset into a collection of jams:

http://isophonics.net/datasets

Note that the structure of an Isophonics dataset (Carole King, The Beatles,
etc) is something like the following:

/* Annotations
    /attribute
        /Artist
            /Album  # -- may not exist --
                /*.lab / *.txt

To parse the entire dataset, you simply need the path to the Isophonics dataset
and an optional output folder.

Example:
./isohpnics_parser.py \
~/datasets/Isophonics/Carole King \
-o ~/datasets/Isophonics/Carole_King_jams

"""

__author__ = "Oriol Nieto"
__copyright__ = "Copyright 2014, Music and Audio Research Lab (MARL)"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "oriol@nyu.edu"

import argparse
import json
import logging
import os
import sys
import time

sys.path.append("..")
import pyjams

# Map of JAMS attributes to Isophonics directories.
ISO_ATTRS = {'beat': 'beat',
             'chord': 'chordlab',
             'key': 'keylab',
             'segment': 'seglab'}


def fill_global_metadata(jam, artist, title):
    """Fills the global metada into the JAMS jam."""
    jam.file_metadata.artist = artist
    jam.file_metadata.duration = -1  # In seconds
    jam.file_metadata.title = title


def fill_annotation_metadata(annot):
    """Fills the annotation metadata."""
    annot.annotation_metadata.corpus = "Isophonics"
    annot.annotation_metadata.version = "1.0"
    annot.annotation_metadata.annotation_tools = "Sonic Visualizer"
    annot.annotation_metadata.annotation_rules = "TODO"  # TODO
    annot.annotation_metadata.validation_and_reliability = "TODO"  # TODO
    annot.annotation_metadata.origin = "Centre for Digital Music"
    annot.annotation_metadata.annotator.name = "TODO"
    annot.annotation_metadata.annotator.email = "TODO"  # TODO


def lab_to_range_annotation(lab_file, annot):
    """Populate a range annotation with a given lab file."""
    start_times, end_times, labels = pyjams.util.read_lab(lab_file, 3)
    pyjams.util.fill_range_annotation_data(
        start_times, end_times, labels, annot)
    fill_annotation_metadata(annot)


def lab_to_event_annotation(lab_file, annot):
    """Populate an event annotation with a given lab file."""
    times, labels = pyjams.util.read_lab(lab_file, 2)
    pyjams.util.fill_event_annotation_data(times, labels, annot)
    fill_annotation_metadata(annot)


def process(in_dir, out_dir):
    """Converts the original Isophonic files into the JAMS format, and saves
    them in the out_dir folder."""
    all_jams = dict()
    output_paths = dict()
    all_labs = pyjams.util.find_with_extension(in_dir, 'lab', 4)
    all_labs += pyjams.util.find_with_extension(in_dir, 'txt', 4)

    for lab_file in all_labs:
        title = pyjams.util.filebase(lab_file)
        if not title in all_jams:
            all_jams[title] = pyjams.JAMS()
            parts = lab_file.replace(in_dir, '').strip('/').split('/')
            fill_global_metadata(all_jams[title], artist=parts[1], title=title)
            output_paths[title] = os.path.join(
                out_dir, *parts[1:]).replace(".lab", ".jams")
            print "%s -> %s" % (title, output_paths[title])

        jam = all_jams[title]
        if ISO_ATTRS['beat'] in lab_file:
            lab_to_event_annotation(lab_file, jam.beat.create_annotation())
        elif ISO_ATTRS['chord'] in lab_file:
            annot = jam.chord.create_annotation()
            lab_to_range_annotation(lab_file, annot)
            jam.file_metadata.duration = annot.data[-1].end
        elif ISO_ATTRS['key'] in lab_file:
            lab_to_range_annotation(lab_file, jam.key.create_annotation())
        elif ISO_ATTRS['segment'] in lab_file:
            annot = jam.segment.create_annotation()
            lab_to_range_annotation(lab_file, annot)
            jam.file_metadata.duration = annot.data[-1].end

    for title in all_jams:
        # Save JAMS
        out_file = output_paths[title]
        pyjams.util.smkdirs(os.path.split(out_file)[0])
        with open(out_file, "w") as fp:
            json.dump(all_jams[title], fp, indent=2)


def main():
    """Main function to convert the dataset into JAMS."""
    parser = argparse.ArgumentParser(
        description="Converts the Isophonics dataset to the JAMS format",
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
    logging.info("Done! Took %.2f seconds." % (time.time() - start_time))

if __name__ == '__main__':
    main()
