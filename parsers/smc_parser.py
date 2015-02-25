#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# CREATED:2015-02-01 15:35:38 by Brian McFee <brian.mcfee@nyu.edu>
'''Parse SMC2 beat tracking data into JAMS format.'''

import sys
import argparse
import os

import librosa
import re
import pandas as pd
import pyjams

from pyjams.util import find_with_extension

__curator__ = dict(name='Matthew Davies', email='mdavies@inescporto.pt')
__corpus__ = 'SMC_MIREX'


def smc_annotation(ann_file):
    '''Create a JAM file and annotation object for beats'''

    # Add metadata + curator
    match = re.match('.*SMC_\d+_(?P<meter>\d_\d_\d)_(?P<annotator>.+).txt',
                     ann_file)

    if not match:
        raise RuntimeError('Could not parse filename {:s}'.format(ann_file))

    curator = pyjams.Curator(**__curator__)

    metadata = pyjams.AnnotationMetadata(curator=curator,
                                         corpus=__corpus__,
                                         annotator={'id':
                                                    match.group('annotator')})

    # Sandbox the following info:
    #   annotator id
    #   metrical interpretation

    annotation = pyjams.Annotation('beat',
                                   annotation_metadata=metadata,
                                   sandbox={'metrical_interpretation':
                                            match.group('meter')})

    # Now load the data

    data = pd.read_csv(ann_file, header=None, squeeze=True)

    for beat_time in data:
        annotation.data.add_observation(time=beat_time,
                                        duration=0,
                                        value=1,
                                        confidence=None)

    return annotation


def smc_tags(tag_file, duration):
    '''Get the tag data for this track as a JAMS annotation'''

    annotation = pyjams.Annotation('tag_open')

    data = []
    for value in list(pd.read_table(tag_file,
                                    header=None,
                                    squeeze=True)):
        if len(value) == 2:
            ann_id, ann_conf = tuple(value)
        else:
            data.append(value)

    curator = pyjams.Curator(**__curator__)

    metadata = pyjams.AnnotationMetadata(curator=curator,
                                         corpus=__corpus__,
                                         annotator={'id': ann_id,
                                                    'confidence': int(ann_conf)})

    annotation.annotation_metadata = metadata

    for tag in data:
        annotation.data.add_observation(time=0,
                                        duration=duration,
                                        value=tag,
                                        confidence=None)

    return annotation


def smc_file_metadata(infile):
    '''Construct a metadata object from an SMC wav file'''

    match = re.match('.*(?P<index>SMC_\d+).wav$', infile)

    if not match:
        raise RuntimeError('Could not index filename {:s}'.format(infile))

    # Get the duration of the track
    y, sr = librosa.load(infile, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)

    # Format duration as time
    metadata = pyjams.FileMetadata(title=match.group('index'),
                                   duration=duration)

    return metadata


def save_jam(output_dir, jam):
    '''Save the output jam'''

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    outfile = os.extsep.join([jam.file_metadata.title, 'jams'])
    outfile = os.path.join(output_dir, outfile)

    print 'Saving {:s}'.format(outfile)
    jam.save(outfile)


def parse_smc(input_dir, output_dir):
    '''Convert smc to jams'''

    # Get a list of the wavs, tags, and txts

    wav_files = find_with_extension(os.path.join(input_dir,
                                                 'SMC_MIREX_Audio'),
                                    'wav', depth=1)

    ann_files = find_with_extension(os.path.join(input_dir,
                                                 'SMC_MIREX_Annotations_05_08_2014'),
                                    'txt', depth=1)

    tag_files = find_with_extension(os.path.join(input_dir,
                                                 'SMC_MIREX_Tags'),
                                    'tag', depth=1)

    # Make sure everything lines up
    assert len(wav_files) == len(ann_files)
    assert len(wav_files) == len(tag_files)

    for wav, ann, tag in zip(wav_files, ann_files, tag_files):
        # Get the file metadata
        metadata = smc_file_metadata(wav)

        # Get the annotation
        beat_annotation = smc_annotation(ann)

        # Get the tags
        tag_annotation = smc_tags(tag, metadata.duration)

        jam = pyjams.JAMS(file_metadata=metadata)
        jam.annotations.append(beat_annotation)
        jam.annotations.append(tag_annotation)

        # Add content path to the top-level sandbox
        jam.sandbox.content_path = os.path.basename(wav)

        # Save the jam
        save_jam(output_dir, jam)


def parse_arguments(args):

    parser = argparse.ArgumentParser(description='SMC2 beat tracking parser')

    parser.add_argument('input_dir',
                        type=str,
                        help='Path to the SMC root directory')

    parser.add_argument('output_dir',
                        type=str,
                        help='Path to output jam files')

    return vars(parser.parse_args(args))


if __name__ == '__main__':
    parameters = parse_arguments(sys.argv[1:])

    parse_smc(**parameters)
