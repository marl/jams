#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''Convert a JAMS object into one or more .lab annotation files'''

import sys
from argparse import ArgumentParser
from collections import defaultdict
import os
import jams


def parse_arguments(args):

    parser = ArgumentParser(description='Parse JAMS annotations into .lab files')

    parser.add_argument('infile', type=str, help='Input JAMS file')
    parser.add_argument('output_prefix', type=str,
                        help='Prefix for output lab files')

    return vars(parser.parse_args(args))


def run(infile='', output_prefix='annotation'):
    '''Do the conversion'''

    jam = jams.load(infile)

    mapping = defaultdict(int)

    for annotation in jam.annotations:
        ns = annotation.namespace
        filename = os.path.extsep.join([output_prefix, ns, str(mapping[ns]), 'lab'])
        mapping[ns] += 1
        annotation.data.to_csv(filename, sep='\t')


if __name__ == '__main__':
    params = parse_arguments(sys.argv[1:])

    run(**params)
