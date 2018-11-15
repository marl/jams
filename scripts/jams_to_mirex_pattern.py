
import csv
import json

x = open('/path/to/file.jams').read()
x = json.loads(x)

record = []

for x in x["annotations"]:
    # looping through the annotators
    metadata = x["annotation_metadata"]
    namespace = x["namespace"]
    
    # annotator names
    anno = metadata["annotator"]
    
    # actual data of annotation
    d = x["data"]

    # open file to write to the MIREX pattern discovery format 
    text_file = open("anno{0}.txt".format(anno), "w")
    text_file.write("Pattern1"+"\n")
    text_file.write("Occ1"+"\n")
    pcount = 1 # keep pattern count
    ocount = 1 # keep pattern occurrence count

    pastpid = 1 # initiatise the pattern count to compare for a change
    pastoid = 1 # initiatise the occurrence count to compare for a change
    
    initpid = d[0]["value"]["pattern_id"]

    for y in d:
        # lopping through the events given an annotator
        time = y["time"]
        dur = y["duration"]

        pid = y["value"]["pattern_id"]

        # update the pattern count when there is a change in the pattern id in the jams file
        if pid != pastpid:
            pcount += 1
            ocount = 0
            text_file.write("Pattern"+str(pcount)+"\n")
            text_file.write("Occ1"+"\n")

        midip = y["value"]["midi_pitch"]
        morphp = y["value"]["morph_pitch"]
        staff = y["value"]["staff"]
        occid = y["value"]["occurrence_id"]

        if occid != pastoid:
            ocount += 1
            text_file.write("Occ"+str(ocount)+"\n")

        c = y["confidence"]

        # keep a record of the last pattern count to compare with for a change
        pastpid = pid
        pastoid = occid

        # write the actual (time, pitch) pairs
        text_file.write(str(time)+", "+str(midip)+"\n")

    text_file.close()
