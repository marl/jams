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
./isohpnics_parser.py ~/datasets/Isophonics/Carole King \
-o ~/datasets/Isophonics/Carole_King_jams

"""

__author__ = "Oriol Nieto"
__copyright__ = "Copyright 2015, Music and Audio Research Lab (MARL)"
__license__ = "MIT"
__version__ = "1.1"
__email__ = "oriol@nyu.edu"

import argparse
import json
import logging
import mir_eval
import os
import six
import sys
import time

import jams

# Map of JAMS attributes to Isophonics directories.
ISO_ATTRS = {'beat': 'beat',
             'chord': 'chordlab',
             'key': 'keylab',
             'segment': 'seglab'}

# Namespace dictionary
NS_DICT = {'beat': 'beat',
           'chord': 'chord_harte',
           'key': 'key_mode',
           'segment': 'segment_isophonics'}


def fill_file_metadata(jam, artist, title):
    """Fills the global metada into the JAMS jam."""
    jam.file_metadata.artist = artist
    jam.file_metadata.duration = None
    jam.file_metadata.title = title


def get_duration_from_annot(annot):
    """Obtains the actual duration from a given annotation."""
    dur = annot.data.iloc[-1].time + annot.data.iloc[-1].duration
    return dur.total_seconds()


def lab_to_range_annotation(lab_file, annot):
    """Populate a range annotation with a given lab file."""
    table = pd.read_table(tag_file, header=None, squeeze=True).dropna(axis=1)
    intervals, labels = mir_eval.io.load_labeled_intervals(lab_file, '\t+|\s+')
    for interval, label in zip(intervals, labels):
        time = float(interval[0])
        dur = float(interval[1]) - time
        if dur <= 0:
            continue
        if label == "E:4":
            label = "E:sus4"
        if label == "Db:6":
            label = "Db:maj6"
        if label == "F#min7":
            label = "F#:min7"
        if label == "B:7sus":
            label = "B:maj7"
        if label == "Db:6/2":
            label = "Db:maj6/2"
        if label == "Ab:6":
            label = "Ab:maj6"
        if label == "F:6":
            label = "F:maj6"
        if label == "D:6":
            label = "D:maj6"
        if label == "G:6":
            label = "G:maj6"
        if label == "A:6":
            label = "A:maj6"
        if label == "E:sus":
            label = "E"
        if label == "E:7sus":
            label = "E:maj7"
        annot.data.add_observation(time=time, duration=dur, value=label)


def lab_to_event_annotation(lab_file, annot):
    """Populate an event annotation with a given lab file."""
    times, labels = mir_eval.io.load_labeled_events(lab_file, '\t+| *')
    for time, label in zip(times, labels):
        time = float(time)
        annot.data.add_observation(time=time, duration=0, value=int(label))


def process(in_dir, out_dir):
    """Converts the original Isophonic files into the JAMS format, and saves
    them in the out_dir folder."""
    all_jams = dict()
    output_paths = dict()
    all_labs = jams.util.find_with_extension(in_dir, 'lab', 5)
    all_labs += jams.util.find_with_extension(in_dir, 'txt', 4)

    for lab_file in all_labs:
        title = jams.util.filebase(lab_file)
        if not title in all_jams:
            all_jams[title] = jams.JAMS()
            parts = lab_file.replace(in_dir, '').strip('/').split('/')
            fill_file_metadata(all_jams[title], artist=parts[1], title=title)
            output_paths[title] = os.path.join(
                out_dir, *parts[1:]).replace(".lab", ".jams")
            six.print_(title, "->", output_paths[title])

        jam = all_jams[title]
        curator = jams.Curator(name="Matthias Mauch",
                               email="m.mauch@qmul.ac.uk")
        ann_meta = jams.AnnotationMetadata(curator=curator,
                                           version=1.0,
                                           corpus="Isophonics",
                                           annotator=None)
        if ISO_ATTRS['beat'] in lab_file:
            annot = jams.Annotation(NS_DICT['beat'],
                                    annotation_metadata=ann_meta)
            lab_to_event_annotation(lab_file, annot)
            jam.annotations.append(annot)
        elif ISO_ATTRS['chord'] in lab_file:
            annot = jams.Annotation(NS_DICT['chord'],
                                    annotation_metadata=ann_meta)
            lab_to_range_annotation(lab_file, annot)
            jam.file_metadata.duration = get_duration_from_annot(annot)
            jam.annotations.append(annot)
        elif ISO_ATTRS['key'] in lab_file:
            annot = jams.Annotation(NS_DICT['key'],
                                    annotation_metadata=ann_meta)
            lab_to_range_annotation(lab_file, annot)
            jam.annotations.append(annot)
        elif ISO_ATTRS['segment'] in lab_file:
            annot = jams.Annotation(NS_DICT['segment'],
                                    annotation_metadata=ann_meta)
            lab_to_range_annotation(lab_file, annot)
            jam.annotations.append(annot)
            jam.file_metadata.duration = get_duration_from_annot(annot)

    for title in all_jams:
        # Save JAMS
        out_file = output_paths[title]
        jams.util.smkdirs(os.path.split(out_file)[0])
        all_jams[title].save(out_file)


if __name__ == '__main__':
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
