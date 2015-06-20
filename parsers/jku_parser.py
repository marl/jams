#!/usr/bin/env python
"""
This script parses the ground truth annotations (csv) into the JAMS format.
"""

__author__ = "Oriol Nieto"
__copyright__ = "Copyright 2015, Music and Audio Research Lab (MARL)"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "oriol@nyu.edu"

import argparse
import csv
import glob
import jams
import logging
import os
import time


def get_bpm(kern_file):
    """Gets the beats per minute from a kern_file."""
    with open(kern_file) as f:
        lines = f.readlines()
        for line in lines:
            if "*MM" in line:
                bpm = float(line.split(" ")[0].split("*MM")[-1])
    return bpm


def get_first_last_onset(csv_file):
    """Gets the first and last onset times."""
    with open(csv_file) as f:
        full_track = list(csv.reader(f))
    first_onset = float(full_track[0][0])
    if first_onset < 0:
        first_onset = abs(first_onset)  # we only store the first onset if it is
                                        # negative (i.e., starts in an upbeat)
    else:
        first_onset = 0
    last_onset = float(full_track[-1][0])
    return first_onset, last_onset


def fill_file_metadata(jam, kern_file, csv_file):
    """Fills the global metada into the JAMS jam."""
    artist = None
    title = None

    # Get first and last onset
    first_onset, last_onset = get_first_last_onset(csv_file)

    # Get the rest of metadata
    bpm = get_bpm(kern_file)
    with open(kern_file) as f:
        lines = f.readlines()
        for line in lines:
            if "!!!COM" in line:
                artist = line.split(": ")[-1]
            if "!!!OTL" in line:
                title = line.split(": ")[-1]

    # Assign metadata
    jam.file_metadata.artist = artist.strip("\n")
    jam.file_metadata.duration = (first_onset + last_onset) / float(bpm)
    jam.file_metadata.title = title.strip("\n")


def get_out_file(patterns, out_dir):
    """Given a set of patterns corresponding to a single musical piece and the
    output directory, get the output file path.

    Parameters
    ----------
    patterns: list of list of strings (files)
        Set of all the patterns with the occurrences of a given piece.
    out_dir: string (path)
        Path to the output directory.

    Returns
    -------
    out_file: string (path)
        Path to the output file.
    """
    assert len(patterns) > 0
    name_split = patterns[0][0].split("/")
    idx_offset = name_split.index("groundTruth") - 1
    return os.path.join(out_dir, name_split[idx_offset + 2] + "-" +
                        name_split[idx_offset + 3] + ".jams")


def find_in_csv(csv_file, occ_file):
    """Finds the data of the occ_file in the csv_file.

    Parameters
    ----------
    csv_file : str
        Path to the main csv_file.
    occ_file : str
        Path to the occurrence csv occ_file.

    Returns
    -------
    start : int
        Start index of the csv_file.
    end : int
        End index of the csv_file.
    """
    # Read CSV files
    with open(occ_file, "r") as f:
        occurrences = list(csv.reader(f))
    with open(csv_file, "r") as f:
        full_track = list(csv.reader(f))

    # Find the indeces
    start = None
    for i, row in enumerate(full_track):
        if row[0] == occurrences[0][0] and row[1] == occurrences[0][1]:
            start = i
            break
    end = None
    for i, row in enumerate(full_track):
        if row[0] == occurrences[-1][0] and row[1] == occurrences[-1][1]:
            end = i + 1     # End correct position + 1
            break

    # Make sure we found the data
    assert start is not None
    assert end is not None

    return start, end


def parse_patterns(csv_file, kern_file, patterns, out_file):
    """Parses the set of patterns and saves the results into the output file.

    Parameters
    ----------
    csv_file : str
        Path to the main csv file from which the pattern is extracted.
    kern_file : str
        Path to the main kern file from which to extract the metadata.
    patterns: list of list of strings (files)
        Set of all the patterns with the occurrences of a given piece.
    out_file: string (path)
        Path to the output file to save the set of patterns in the MIREX
        format.
    """
    # Create JAMS and add some metada
    jam = jams.JAMS()
    curator = jams.Curator(name="Tom Collins", email="tom.collins@dmu.ac.uk")
    fill_file_metadata(jam, kern_file, csv_file)
    ann_meta = jams.AnnotationMetadata(curator=curator,
                                       version="August2013",
                                       corpus="JKU Development Dataset")

    # Create actual annotation
    annot = jams.Annotation(namespace="pattern_jku",
                            annotation_metadata=ann_meta)

    # Get bpm and first and last onsets
    bpm = get_bpm(kern_file)
    first_onset, last_onset = get_first_last_onset(csv_file)

    pattern_n = 1
    for pattern in patterns:
        occ_n = 1
        for occ_file in pattern:
            start, end = find_in_csv(csv_file, occ_file)
            with open(csv_file, "r") as f:
                file_reader = list(csv.reader(f))
                for i in range(start, end):
                    value = {
                        "midi_pitch": float(file_reader[i][1]),
                        "morph_pitch": float(file_reader[i][2]),
                        "staff": int(float(file_reader[i][4])),  # Hack to convert 0.000000000 into an int
                        "pattern_id": pattern_n,
                        "occurrence_id": occ_n
                    }
                    # Transform onset to time
                    time = (first_onset + float(file_reader[i][0])) / float(bpm)
                    annot.data.add_observation(time=time,
                                               duration=float(file_reader[i][3]),
                                               value=value)
            occ_n += 1
        pattern_n += 1

    # Annotation to the jams
    jam.annotations.append(annot)

    # Save file
    jam.save(out_file)


def get_gt_patterns(annotators):
    """Obtains the set of files containing the patterns and its occcurrences
    given the annotator directories.

    Parameters
    ----------
    annotators: list of strings (files)
        List containing a set of paths to all the annotators of a given piece.

    Returns
    -------
    P: list of list of strings (files)
       Paths to all the patterns with all the occurrences for the current
       annotator. e.g. P = [[pat1_occ1, pat1_occ2],[pat2_occ1, ...],...]
    """
    P = []
    for annotator in annotators:
        # Get all the patterns from this annotator
        patterns = glob.glob(os.path.join(annotator, "*"))
        for pattern in patterns:
            if os.path.isdir(pattern):
                # Get all the occurrences for the current pattern
                occurrences = glob.glob(os.path.join(pattern, "occurrences",
                                                     "csv", "*.csv"))
                P.append(occurrences)
    return P


def process(jku_dir, out_dir):
    """Main process to parse the ground truth csv files.

    Parameters
    ----------
    jku_dir: string
        Directory where the JKU Dataset is located.
    out_dir: string
        Directory in which to put the parsed files.
    """
    # Check if output folder and create it if needed:
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Get all the music pieces in the ground truth
    pieces = glob.glob(os.path.join(jku_dir, "groundTruth", "*"))

    # Two types of patterns for each piece
    types = ["monophonic", "polyphonic"]

    # Main loop to retrieve all the patterns from the GT
    all_patterns = []
    csv_files = []
    kern_files = []
    for piece in pieces:
        logging.info("Reading piece %s" % piece)
        for type in types:
            # Get the main csv and kern file
            csv_files.append(glob.glob(os.path.join(piece, type, "csv",
                                                    "*.csv"))[0])
            kern_files.append(glob.glob(os.path.join(piece, type, "kern",
                                                    "*.krn"))[0])

            # Get all the annotators for the current piece
            annotators = glob.glob(os.path.join(piece, type,
                                                "repeatedPatterns", "*"))

            # Based on the readme.txt of JKU, these are the valid annotators
            # (thanks Colin! :-)
            if type == "polyphonic":
                valid_annotators = ['barlowAndMorgensternRevised',
                                    'bruhn',
                                    'schoenberg',
                                    'sectionalRepetitions',
                                    'tomCollins']
                for annotator in annotators:
                    if os.path.split(annotator)[1] not in valid_annotators:
                        annotators.remove(annotator)

            all_patterns.append(get_gt_patterns(annotators))

    # For the patterns of one given file, parse them into a single file
    for csv_file, kern_file, patterns in zip(csv_files, kern_files,
                                             all_patterns):
        logging.info("Parsing file %s" % os.path.basename(csv_file))
        out_file = get_out_file(patterns, out_dir)
        parse_patterns(csv_file, kern_file, patterns, out_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        "Parses the ground truth in csv format into the MIREX format",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("jku_dir",
                        action="store",
                        help="Input JKU dataset dir")
    parser.add_argument("out_dir",
                        action="store",
                        help="Output dir")
    args = parser.parse_args()
    start_time = time.time()

    # Setup the logger
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s',
        level=logging.INFO)

    # Run the algorithm
    process(args.jku_dir, args.out_dir)

    # Done!
    logging.info("Done! Took %.2f seconds." % (time.time() - start_time))
