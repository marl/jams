#!/usr/bin/env python
'''Convert a jams file into one or more lab files.'''

import argparse
import collections
import sys
import os
import json
import pandas as pd

import jams


def get_output_name(output_prefix, namespace, index):
    '''Get the output name (prefix)

    Parameters
    ----------
    output_prefix : str
        The path prefix of the target filename

    namespace : str
        The namespace of the annotation in question

    index : int
        The index number of this annotation within the namespace

    Returns
    -------
    output_name : str
        "output_prefix__namespace__index"
    '''
    return '{:s}__{:s}__{:02d}'.format(output_prefix, namespace, index)


def get_comments(jam, ann):
    '''Get the metadata from a jam and an annotation, combined as a string.

    Parameters
    ----------
    jam : JAMS
        The jams object

    ann : Annotation
        An annotation object

    Returns
    -------
    comments : str
        The jam.file_metadata and ann.annotation_metadata, combined and serialized
    '''
    jam_comments = jam.file_metadata.__json__
    ann_comments = ann.annotation_metadata.__json__
    return json.dumps({'metadata': jam_comments,
                       'annotation metadata': ann_comments},
                      indent=2)


def lab_dump(ann, comment, filename, sep, comment_char):
    '''Save an annotation as a lab/csv.

    Parameters
    ----------
    ann : Annotation
        The annotation object

    comment : str
        The comment string header

    filename : str
        The output filename

    sep : str
        The separator string for output

    comment_char : str
        The character used to denote comments
    '''

    intervals, values = ann.to_interval_values()

    frame = pd.DataFrame(columns=['Time', 'End Time', 'Label'],
                         data={'Time': intervals[:, 0],
                               'End Time': intervals[:, 1],
                               'Label': values})

    with open(filename, 'w') as fdesc:
        for line in comment.split('\n'):
            fdesc.write('{:s}  {:s}\n'.format(comment_char, line))

        frame.to_csv(path_or_buf=fdesc, index=False, sep=sep)


def convert_jams(jams_file, output_prefix, csv=False, comment_char='#', namespaces=None):
    '''Convert jams to labs.

    Parameters
    ----------
    jams_file : str
        The path on disk to the jams file in question

    output_prefix : str
        The file path prefix of the outputs

    csv : bool
        Whether to output in csv (True) or lab (False) format

    comment_char : str
        The character used to denote comments

    namespaces : list-like
        The set of namespace patterns to match for output
    '''

    if namespaces is None:
        raise ValueError('No namespaces provided. Try ".*" for all namespaces.')

    jam = jams.load(jams_file)

    # Get all the annotations
    # Filter down to the unique ones
    # For each annotation
    #     generate the comment string
    #     generate the output filename
    #     dump to csv

    # Make a counter object for each namespace type
    counter = collections.Counter()

    annotations = []

    for query in namespaces:
        annotations.extend(jam.search(namespace=query))

    if csv:
        suffix = 'csv'
        sep = ','
    else:
        suffix = 'lab'
        sep = '\t'

    for ann in annotations:
        index = counter[ann.namespace]
        counter[ann.namespace] += 1
        filename = os.path.extsep.join([get_output_name(output_prefix,
                                                        ann.namespace,
                                                        index),
                                        suffix])

        comment = get_comments(jam, ann)

        # Dump to disk
        lab_dump(ann, comment, filename, sep, comment_char)


def parse_arguments(args):
    '''Parse arguments from the command line'''
    parser = argparse.ArgumentParser(description='Convert JAMS to .lab files')

    parser.add_argument('-c',
                        '--comma-separated',
                        dest='csv',
                        action='store_true',
                        default=False,
                        help='Output in .csv instead of .lab')

    parser.add_argument('--comment', dest='comment_char', type=str, default='#',
                        help='Comment character')

    parser.add_argument('-n',
                        '--namespace',
                        dest='namespaces',
                        nargs='+',
                        default=['.*'],
                        help='One or more namespaces to output.  Default is all.')

    parser.add_argument('jams_file',
                        help='Path to the input jams file')

    parser.add_argument('output_prefix', help='Prefix for output files')

    return vars(parser.parse_args(args))


if __name__ == '__main__':

    convert_jams(**parse_arguments(sys.argv[1:]))
