#!/usr/bin/env python

import jams
import sys


def import_chord_jams(infile, outfile):

    # import_lab returns a new jams object,
    # and a handle to the newly created annotation
    chords = jams.util.import_lab('chord', infile)

    # Infer the track duration from the end of the last annotation
    duration = max([obs.time + obs.duration for obs in chords])

    chords.time = 0
    chords.duration = duration

    # Create a jams object
    jam = jams.JAMS()
    jam.file_metadata.duration = duration
    jam.annotations.append(chords)

    # save to disk
    jam.save(outfile)


if __name__ == '__main__':

    infile, outfile = sys.argv[1:]
    import_chord_jams(infile, outfile)
