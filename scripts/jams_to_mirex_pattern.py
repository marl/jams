
#!/usr/bin/env python
'''Convert JAMS to MIREX pattern discovery format

Example usage:

./jams_to_mirex_pattern.py /path/to/file.jams outputname
'''

import json
import sys
from argparse import ArgumentParser
import jams

def parse_arguments(args):

    parser = ArgumentParser(description='Parse JAMS annotations into the MIREX Pattern Discovery task format')

    parser.add_argument('infile', type=str, help='Input JAMS file')
    parser.add_argument('output_prefix', type=str,
                        help='Prefix for output lab files')

    return vars(parser.parse_args(args))

def run(infile='', output_prefix='annotation'):
    with open(infile, 'r') as fdesc:
        x = json.load(fdesc)

    for elem in x["annotations"]:
        # looping through the annotators

        metadata = elem["annotation_metadata"]
        anno = metadata["annotator"]
        d = elem["data"]

        with open('{1}_{0}.txt'.format(anno, output_prefix), 'w') as text_file:
            text_file.write("Pattern1" + "\n")
            text_file.write("Occ1" + "\n")

            pcount = 1
            ocount = 1

            initpid = d[0]["value"]["pattern_id"]
            initocc = d[0]["value"]["occurrence_id"]

            pastpid = initpid
            pastoid = initocc

            for y in d:
                # lopping through the events given an annotator
                time = y["time"]

                pid = y["value"]["pattern_id"]

                if pid != pastpid:
                    pcount += 1
                    ocount = 1
                    text_file.write("Pattern"+str(pcount)+"\n")
                    text_file.write("Occ"+str(ocount)+"\n")

                midip = y["value"]["midi_pitch"]
                occid = y["value"]["occurrence_id"]

                if occid != pastoid:
                    ocount += 1
                    text_file.write("Occ"+str(ocount)+"\n")

                pastpid = pid
                pastoid = occid

                text_file.write(str(time)+", "+str(midip)+"\n")



if __name__ == '__main__':
    params = parse_arguments(sys.argv[1:])

    run(**params)
