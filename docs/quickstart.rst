***************
Getting started
***************

Creating a JAMS data structure from scratch
===========================================
First, create the top-level JAMS container:

    >>> import jams
    >>> jam = jams.JAMS()

A track in JAMS must have a duration (in seconds).  For this example, we'll make up a fake number, but in
reality, you would compute the track duration from the source audio.

    >>> jam.file_metadata.duration = 8.0

Now we can create a beat annotation:

    >>> ann = jams.Annotation(namespace='beat', time=0, duration=jam.file_metadata.duration)
    >>> ann.append(time=0.33, duration=0.0, confidence=1, value=1)

Then, we'll update the annotation's metadata by directly setting its fields:

    >>> ann.annotation_metadata = jams.AnnotationMetadata(data_source='Well paid students')
    >>> ann.annotation_metadata.curator = jams.Curator(name='Rincewind',
    ...                                                email='rincewind@unseen.edu')

Add our new annotation to the jam:

    >>> jam.annotations.append(ann)

We can update the annotation at any time, and add a new observation:

    >>> ann.append(time=0.66, duration=0.0, confidence=1, value=1)


Once you've added all your data, you can serialize the annotation to a string:

    >>> jam.dumps(indent=2)
    {
      "sandbox": {}, 
      "annotations": [
        {
          "data": [
            {
              "duration": 0.0, 
              "confidence": 1.0, 
              "value": 1.0, 
              "time": 0.33
            }, 
            {
              "duration": 0.0, 
              "confidence": 1.0, 
              "value": 1.0, 
              "time": 0.66
            }
          ], 
          "annotation_metadata": {
            "annotation_tools": "", 
            "curator": {
              "name": "Rincewind", 
              "email": "rincewind@unseen.edu"
            }, 
            "annotator": {}, 
            "version": "", 
            "corpus": "", 
            "annotation_rules": "", 
            "validation": "", 
            "data_source": "Well paid students"
          }, 
          "namespace": "beat", 
          "sandbox": {}
        }
      ], 
      "file_metadata": {
        "jams_version": "0.2.0", 
        "title": "", 
        "identifiers": {}, 
        "release": "", 
        "duration": 8.0, 
        "artist": ""
      }
    }

Or save to a file using the built-in save function:

    >>> jam.save("these_are_still_my.jams")


Reading a JAMS file
===================
Assuming you already have a JAMS file on-disk, say at 'these_are_also_my.jams',
you can easily read it back into memory:

    >>> another_jam = jams.load('these_are_also_my.jams')
