#!/usr/bin/env python

import jams
import sys

def import_chord_jams(infile, outfile):

    # import_lab returns a new jams object,
    # and a handle to the newly created annotation
    jam, chords = jams.util.import_lab('chord', infile)

    # Infer the track duration from the end of the last annotation
    duration = (chords.data['time'] + chords.data['duration']).max()

    # this timing will be in pandas timedelta.
    # calling duration.total_seconds() converts to float
    jam.file_metadata.duration = duration.total_seconds()

    chords.time = 0
    chords.duration = duration.total_seconds()

    # save to disk
    jam.save(outfile)


if __name__ == '__main__':

    infile, outfile = sys.argv[1:]
    import_chord_jams(infile, outfile)

