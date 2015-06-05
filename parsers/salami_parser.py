#!/usr/bin/env python
"""
This script parses the SALAMI v2.0 dataset into the JAMS format.

Usage example:
    ./salami_parser.py salami-data-public/ OutputSalamiJAMS
"""

__author__ = "Oriol Nieto"
__copyright__ = "Copyright 2015, Music and Audio Research Lab (MARL)"
__license__ = "MIT"
__version__ = "1.1"
__email__ = "oriol@nyu.edu"

import argparse
import csv
import logging
import numpy as np
import os
import sys
import time

import jams


def fix_labels(label):
    """Fixes the given labels to comply the SALAMI guidelines and JAMS
    namespace."""
    label = label.lower()
    if label == "a'/a''":
        label = "no_function"
    if label == "b/c'":
        label = "no_function"
    if label == "bagpipes":
        label = "instrumental"
    if label == "banjo":
        label = "instrumental"
    if label == "code":
        label = "coda"
    if label == "dialog":
        label = "spoken"
    if label == "female":
        label = "voice_female"
    if label == "first":
        label = "main theme"
    if label == "guitar":
        label = "instrumental"
    if label == "hammond":
        label = "instrumental"
    if label == "main_theme":
        label = "main theme"
    if label == "male":
        label = "voice_male"
    if label == "muted":
        label = "fade-out"
    if label == "organ":
        label = "instrumental"
    if label == "out":
        label = "outro"
    if label == "piano":
        label = "instrumental"
    if label == "recap":
        label = "recapitulation"
    if label == "secondary_theme":
        label = "secondary theme"
    if label == "spoken_voice":
        label = "spoken"
    if label == "stage_speaking":
        label = "spoken"
    if label == "steel":
        label = "instrumental"
    if label == "tag":
        label = "head"
    if label == "trumpet":
        label = "instrumental"
    if label == "third":
        label = "third theme"
    if label == "violin":
        label = "instrumental"
    if label == "vocalizations":
        label = "voice"
    if label == "vocals":
        label = "voice"
    if label == "w/dialog":
        label = "spoken"
    return label


def parse_annotation(jam, path, annotation_id, level, metadata):
    """Parses one annotation for the given level

    Parameters
    ----------
    jam: object
        The top-level JAMS object.
    path: str
        path to the track in the SALAMI dataset.
    annotation_id: int
        Whether to use the first or the second annotation.
    level: str
        Level of annotation.
    metadata: list
        List containing the information of the CSV file for the current track.
    """
    level_dict = {
        "function": "_functions",
        "large_scale": "_uppercase",
        "small_scale": "_lowercase"
    }
    namespace_dict = {
        "function": "segment_salami_function",
        "large_scale": "segment_salami_upper",
        "small_scale": "segment_salami_lower"
    }

    # File to open
    file_path = os.path.join(path, "parsed",
                             "textfile" + str(annotation_id) +
                             level_dict[level] + ".txt")

    # Open file
    try:
        f = open(file_path, "r")
    except IOError:
        logging.warning("Annotation missing in %s", file_path)
        return

    # Annotation Metadata
    curator = jams.Curator(name="Jordan Smith",
                           email="jblsmith@gmail.com")
    annotator = {
        "name": metadata[annotation_id + 1],
        "submission_date": metadata[annotation_id + 15]
    }
    ann_meta = jams.AnnotationMetadata(curator=curator,
                                       version="2.0",
                                       corpus="SALAMI",
                                       annotator=annotator,
                                       data_source=metadata[1],
                                       annotation_tools="Sonic Visualizer")

    # Create Annotation
    annot = jams.Annotation(namespace=namespace_dict[level],
                            annotation_metadata=ann_meta)

    # Actual Data
    lines = f.readlines()
    for i, line in enumerate(lines[:-1]):
        start_time, label = line.strip("\n").split("\t")
        end_time = lines[i + 1].split("\t")[0]
        start_time = float(start_time)
        end_time = float(end_time)
        dur = end_time - start_time
        if start_time - end_time == 0:
            continue

        if level == "function":
            label = fix_labels(label)

        annot.data.add_observation(time=start_time, duration=dur, value=label)
    f.close()

    # Add annotation to the jams
    jam.annotations.append(annot)


def fill_global_metadata(jam, metadata, dur):
    """Fills the global metada into the JAMS jam."""
    meta = jams.FileMetadata(title=metadata[7],
                             artist=metadata[8],
                             duration=dur,
                             jams_version=jams.version.version)
    jam.file_metadata = meta


def create_annotations(jam, path, annotation_id, metadata):
    """Fills the JAMS annot annotation given a path to the original
    SALAMI annotations. The variable "annotator" let's you choose which
    SALAMI annotation to use.

    Parameters
    ----------
    jam: object
        The top-level JAMS object.
    path: str
        Patht to the file containing the references.
    annotation_id: int
        1 or 2 depending on which annotation to use
    metadata: list
        List containing the information of the CSV file for the current track.
    """
    # Parse all level annotations
    levels = ["function", "large_scale", "small_scale"]
    [parse_annotation(jam, path, annotation_id, level, metadata)
        for level in levels]


def get_duration(jam):
    """Obtains the duration from the jams annotations.

    Parameters
    ----------
    jam : object
        JAMS object with at least one annotation.

    Returns
    -------
    dur : float
        Duration of the file, by taking the max last boundary of all
        annotations (in seconds).
    """
    durs = []
    for annotation in jam.annotations:
        durs.append(annotation.data["time"].iloc[-1].total_seconds() +
                    annotation.data["duration"].iloc[-1].total_seconds())
    return np.max(durs)


def create_JAMS(in_dir, metadata, out_file):
    """Creates a JAMS file given the path to a SALAMI track.

    Parameters
    ----------
    in_dir : str
        Path to the input directory
    metadata : str
        Metadata read from the CSV file
    out_file : str
        Output JAMS file
    """
    path = os.path.join(in_dir, "annotations", metadata[0], )

    # Sanity check
    if not os.path.exists(path):
        logging.warning("Path not found %s", path)
        return

    # New JAMS and annotation
    jam = jams.JAMS()

    # Create Annotations if they exist
    # Maximum 3 annotations per file
    for annotation_id in range(1, 4):
        if os.path.isfile(
            os.path.join(path, "textfile" + str(annotation_id) + ".txt")):
            create_annotations(jam, path, annotation_id, metadata)

    # Get the duration from the annotations
    dur = get_duration(jam)

    # Global file metadata
    fill_global_metadata(jam, metadata, dur)

    # Save JAMS
    jam.save(out_file)


def process(in_dir, out_dir):
    """Converts the original SALAMI files into the JAMS format, and saves
    them in the out_dir folder."""

    # Check if output folder and create it if needed:
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Open CSV with metadata
    with open(os.path.join(in_dir, "metadata", "metadata.csv")) as fh:
        csv_reader = csv.reader(fh)
        for i, metadata in enumerate(csv_reader):
            if metadata[0] == "SONG_ID":
                continue
            # Create a JAMS file for this track
            logging.info("Parsing file %s..." % metadata[0])
            create_JAMS(in_dir, metadata,
                        os.path.join(out_dir,
                            os.path.basename(metadata[0]) + ".jams"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        "Converts the SALAMI dataset to the JAMS format",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("in_dir",
                        action="store",
                        help="SALAMI main folder")
    parser.add_argument("out_dir",
                        action="store",
                        help="Output JAMS folder")
    args = parser.parse_args()
    start_time = time.time()

    # Setup the logger
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)

    # Run the parser
    process(args.in_dir, args.out_dir)

    # Done!
    logging.info("Done! Took %.2f seconds." % (time.time() - start_time))
