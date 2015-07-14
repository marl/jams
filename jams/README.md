pyjams
=======

Python library for loading and creating JAMS files.

Usage
-------------

### To load a JAMS file:
```
import pyjams
jam = pyjams.load('these_are_my.jams')
print jam
```

### To create a new JAMS file:

First create an empty JAMS object.
```
import pyjams
jam = pyjams.JAMS()
```
To add, for example, a beat annotation:
```
beat_annot = jam.beat.create_annotation()
beat = beat_annot.create_datapoint()
beat.time.value = 0.33
beat.time.confidence = 1.0
beat.label.value = "1"
beat.label.confidence = 0.75
```
To update the annotation's metadata:
```
beat_annot.annotation_metadata.data_source = "Poorly paid students"
beat_annot.annotation_metadata.curator.name = "My Name"
beat_annot.annotation_metadata.curator.email = "somebody@aol.com"
```
To see what's there:
```
print jam
```
To save the new jam to a file:
```
pyjams.save(jam, "these_are_still_my.jams")
```
