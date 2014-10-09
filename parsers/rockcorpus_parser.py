#!/usr/bin/env python
"""
Translates the Rock Corpus Dataset chord and melody annotations to a set of JAMS files.

The original data is found online at the following URL:
    http://theory.esm.rochester.edu/rock_corpus/

To parse the entire dataset, you simply need to provide the path to the
unarchived folders.

Example:


NOTES:

There are a number of issues discovered when attempting to convert this dataset to JAMS format:

1. The harmony files are assumed to have been expanded using the expand6 utility provided by the original annotators. 
Similarly, the melody files are assumed to have been expanded using the process-mel5 utility. 

2. The units of time used in both the harmony and melody annotations are measures 
(so, for example, "1.5" indicates a time half way through the second measure). 
Note that timing data can be added (e.g., using the add-timings utility), but only measure times are provided by the annotators, so 
times are approximate for events occurring at times other than beginnings of measures. Note that running add-timings will modify the harmony annotation file, 
and change the meaning of the first and second columns. Before add-timings is run, the first and second columns are the start and end times of the chord (in measures);
after add-timings is run, the first and second columns are start time in seconds and start time in measures.

3. Melodic events are represented by the MIDI note number (where middle C = 60). Because the original dataset does not inlcude duration information, 
we assume that the end time of a given note is equal to the start time of the following note. 
Harmonic events are represented by Roman Numeral, with the secondary value being the pitch class of the current key. The original
annotations provide more information, i.e. chromatic root, diatonic root, and absolute root (c.f. http://theory.esm.rochester.edu/rock_corpus/programs.html#P1).
This information can be derived from the Roman Numeral and key.

4. The expanded harmony files have an irregular format. The last line is always 3 columns; all other lines are 7 columns (regardless of whether or not add-timings has been run).

5. Only one curator is currently allowed, but this dataset seems to have two (David Temperley and Trevor de Clercq).

6. We assume that the Rock Corpus directory contains the sub-directories rs200_harmony_clt (containing the expanded harmony annotations) and rs200_melody_nlt (containing the expanded melody annotations).
This directory should also contain the file "audio_sources.txt" at the top level.

"""

__author__ = "J. P. Forsyth"
__copyright__ = "Copyright 2014, Music and Audio Research Lab (MARL)"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "jpf211@nyu.edu"

import argparse
import json
import logging
import os
import sys
import tempfile
import time

sys.path.append("..")
import pyjams


AUDIO_SOURCES_FILE = 'audio_sources.txt'
ANNOTATORS = { 'dt' : 'David Temperley', 'tdc' : 'Trevor de Clercq' }

MELODY_DIR = 'rs200_melody_nlt'
HARMONY_DIR = 'rs200_harmony_clt'
TIMING_DATA_DIR = 'timing_data'


def fill_annotation_metadata(annot,annotator,sandbox_text=None):
    """Fills the annotation metadata."""
    annot.annotation_metadata.corpus = "Rock Corpus"
    annot.annotation_metadata.version = "2.1"
    annot.annotation_metadata.annotation_rules = ""
    annot.annotation_metadata.data_source = "music faculty"
    annot.annotation_metadata.curator = pyjams.Curator(name="David Temperley, Trevor de Clercq",
                                                       email="dtemperley@esm.rochester.edu, trevor.declercq@gmail.com")
    annot.annotation_metadata.annotator = annotator
    if not sandbox_text is None:
        annot.sandbox = sandbox_text
 
def fill_event_annotation_data(times, labels, secondary_values, event_annotation):
    """Add a collection of data to an event annotation with secondary values (in-place).

    Parameters
    ----------
    times: list of scalars
        Event times in seconds.
    labels: list
        The corresponding labels for each event.
    secondary_values:
        List of secondary values for each event.
    event_annotation: EventAnnotation
        An instantiated event annotation to populate.
    """
    for t, l, s in zip(times, labels, secondary_values):
        data = event_annotation.create_datapoint()
        data.time.value = t
        data.label.value = l
        data.label.secondary_value = s


def fill_range_annotation_data(start_times, end_times, labels, secondary_values,
                               range_annotation):
    """Add a collection of data to a range annotation (in-place).

    Parameters
    ----------
    start_times: list of scalars
        Start times of each range, in seconds.
    end_times: list of scalars
        End times of each range, in seconds.
    labels: list
        The corresponding labels for each range.
    range_annotation: RangeAnnotation
        An instantiated range annotation to populate.
    """
    for t0, t1, l, s in zip(start_times, end_times, labels, secondary_values):
        data = range_annotation.create_datapoint()
        data.start.value = t0
        data.end.value = t1
        data.label.value = l
        data.label.secondary_value = s



def read_harmony_lab(filename,timing_added):
    """ read a .clt harmony file. all lines will have 7 columns with the exception of the last
    one, which has 3, so we have to parse everything but the last line and the last line
    separately. """

    text = pyjams.util.load_textlist(filename=filename)

    # write a temp file with all lines except last one 
    fid, fpath = tempfile.mkstemp(suffix='.txt')
    fhandle = os.fdopen(fid, 'w')
    for i in range(len(text)-1):
        fhandle.writelines(text[i]+'\n')
    fhandle.close()

    # now parse it correctly
    if timing_added:
        _, start_times, chord_labels, _ , _ , keys, _  = pyjams.util.read_lab(fpath, 7)

    else:
        start_times, end_times, chord_labels, _ , _ , keys, _ = pyjams.util.read_lab(fpath, 7)    

    # and delete temp file
    os.remove(fpath)

    # if timing information has been added, need to get end times
    if timing_added:
        end_times = start_times[1:]
        final_t = float(text[-1].split('\t')[1])
        end_times.append(final_t)

    return start_times, end_times, chord_labels, keys


def get_audio_sources_info(audio_sources_file):
    """ get information regarding audio source files. 
    Returns a dictionary that maps song names to artist and album """

    data = pyjams.util.read_lab(audio_sources_file, 3, delimiter='\t')

    # make a dictionary so we can look up by song name
    songs = {}
    N = len(data[0])
    for n in range(N):
        name = str(data[0][n])
        songs[name] = { 'artist' : str(data[1][n]), 'album' : str(data[2][n]) }

    return songs


def parse_harmony_clt_file(harmony_file, jam, annotator, timing_added):
    """ given a harmony .clt file, add annotations to jam """

    start_times, end_times, chord_labels, keys = read_harmony_lab(filename=harmony_file,timing_added=timing_added)

    chord_annot = jam.chord.create_annotation()
    chord_annot.annotation_metadata.annotator = annotator

    jam.file_metadata.duration = end_times[-1]

    fill_range_annotation_data(start_times=start_times,end_times=end_times, labels=chord_labels, secondary_values=keys, range_annotation=chord_annot)
    fill_annotation_metadata(chord_annot,annotator,sandbox_text="chord label secondary value indicates pitch class of current key. time units are measures.")


def parse_melody_nlt_file(melody_file, jam, annotator, timing_added):
    """ parse a melody .nlt file, and add annotations to jam """

    if timing_added:
        _ , times, note_events, scale_degrees  = pyjams.util.read_lab(melody_file, 4)
    else:
        times, note_events, scale_degrees  = pyjams.util.read_lab(melody_file, 3)        

    if len(times) == 0:
        logging.warning('skipping:'+melody_file+' (no melody transcription available).')
        return
    end_times = times[1:]
    end_times.append(jam.file_metadata.duration)

    note_annot = jam.note.create_annotation()
    note_annot.annotation_metadata.annotator = annotator
    fill_range_annotation_data(start_times=times, end_times=end_times, labels=note_events, secondary_values=scale_degrees, range_annotation=note_annot)
    fill_annotation_metadata(note_annot,annotator,sandbox_text="note label secondary value indicates scale degree of melody note. time units are measures.")


def parse_timing_file(timing_file, jam):
    """ parse a timing data file """

    times, measures = pyjams.util.read_lab(timing_file,2)

    # represent measures as beat annotation. this means that all labels are "1.0", since all events indicate start of measure
    labels = len(times)*[1.0]

    beat_annot = jam.beat.create_annotation()
    fill_event_annotation_data(times=times, labels=labels, secondary_values=measures, event_annotation=beat_annot)
    fill_annotation_metadata(beat_annot,"",sandbox_text="beat label secondary value indicates measure number.")


def create_JAMS(in_dir, out_dir, filebase, artist, album, timing_added=True):
    """ add all annotations for given song to a JAMS file """

    jam = pyjams.JAMS()

    # add file level metadata
    jam.file_metadata.artist = artist
    jam.file_metadata.title = filebase.replace('_',' ').title()
    jam.file_metadata.release = album.replace('\t',' ')

    for a in ANNOTATORS.keys():

        # two harmony annotations
        harmony_file = os.path.join(in_dir,HARMONY_DIR,filebase+'_'+a+'.clt')
        if not os.path.exists(harmony_file):
            logging.error('file:'+harmony_file+'not found. Skipping!')
            return
        else:
            parse_harmony_clt_file(harmony_file=harmony_file, jam=jam, annotator=ANNOTATORS[a], timing_added=timing_added)

        # one melody annotation (with annotator indicated in file name)
        melody_file = os.path.join(in_dir,MELODY_DIR,filebase+'_'+a+'.nlt')
        if os.path.exists(melody_file):
            parse_melody_nlt_file(melody_file=melody_file, jam=jam, annotator=ANNOTATORS[a], timing_added=timing_added)

    # one timing file (no indication of annotator)
    timing_file = os.path.join(in_dir,TIMING_DATA_DIR,filebase+'.tim')
    parse_timing_file(timing_file=timing_file, jam=jam)

    # Save JAMS
    out_file = os.path.join(out_dir,filebase+'.jams')
    with open(out_file, "w") as fp:
        json.dump(jam, fp, indent=2)


def process(in_dir, out_dir):
    """ do the conversion """

    pyjams.util.smkdirs(out_dir)

    song_map = get_audio_sources_info(os.path.join(in_dir,AUDIO_SOURCES_FILE))

    for songname,info in song_map.items():
        logging.info('processing '+songname)
        create_JAMS(in_dir=in_dir,out_dir=out_dir,filebase=str(songname),artist=info['artist'],album=info['album'])


def main():
    """Main function to convert the dataset into JAMS."""
    parser = argparse.ArgumentParser(
        description="Converts the Rock Corpus dataset to the JAMS format",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("in_dir",
                        action="store",
                        help="RockCorpus main folder")
    parser.add_argument("-o",
                        action="store",
                        dest="out_dir",
                        # TODO(ejhumphrey): This should be a config, no?
                        default="outJAMS",
                        help="Output JAMS folder")
    args = parser.parse_args()
    start_time = time.time()

    # Setup the logger
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

    # Run the parser
    process(args.in_dir, args.out_dir)

    # Done!
    logging.info("Done! Took %.2f seconds.", time.time() - start_time)

if __name__ == '__main__':
    main()

