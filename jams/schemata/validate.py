#!/usr/bin/env python
'''Validator script for jams files'''

import argparse
import sys
import json
import jsonschema


def process_arguments(args):
    '''Argument parser'''
    parser = argparse.ArgumentParser(description='JAMS schema validator')

    parser.add_argument('schema_file',
                        action='store',
                        help='path to the schema file')
    parser.add_argument('jams_files',
                        action='store',
                        nargs='+',
                        help='path to one or more JAMS files')

    return vars(parser.parse_args(args))


def load_json(filename):
    '''Load a json file'''
    with open(filename, 'r') as fdesc:
        return json.load(fdesc)


def validate(schema_file=None, jams_files=None):
    '''Validate a jams file against a schema'''

    schema = load_json(schema_file)

    for jams_file in jams_files:
        try:
            jams = load_json(jams_file)
            jsonschema.validate(jams, schema)
            print '{:s} was successfully validated'.format(jams_file)
        except jsonschema.ValidationError as exc:
            print '{:s} was NOT successfully validated'.format(jams_file)

            print exc


if __name__ == '__main__':
    validate(**process_arguments(sys.argv[1:]))
