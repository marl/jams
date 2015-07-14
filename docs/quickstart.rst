1. Creating a JAMS data structure from scratch
----------------------------------------------
First, create the top-level JAMS container:

  >>> import jams
  >>> jam = jams.JAMS()

 Now we can create a beat annotation:

  >>> annot = jam.beat.create_annotation()
  >>> annot.append(time=0.33,
                   duration=0.0,
                   confidence=1.0,
                   value="1")


Then, we'll update the annotation's metadata by directly setting its fields:

  >>> annot.annotation_metadata.data_source = "Poorly paid students"
  >>> annot.annotation_metadata.curator.name = "My Name"
  >>> annot.annotation_metadata.curator.email = "somebody@aol.com"


And now a second time, cause this is our house (and we can do what we want):

  >>> annot.append(time=0.66,
                   duration=0.0,
                   confidence=1.0,
                   value="1")


Once you've added all your data, you can serialize the annotation to a file
with the built-in `json` library:

  >>> import json
  >>> with open("these_are_my.jams", 'w') as fp:
          json.dump(jam, fp, indent=2)

Or, less verbosely, using the built-in save function:

  >>> jams.save(jam, "these_are_still_my.jams")


2. Reading a Jams file
----------------------
Assuming you already have a JAMS file on-disk, say at 'these_are_also_my.jams',
you can easily read it back into memory:

  >>> another_jam = jams.load('these_are_also_my.jams')


And that's it!

  >>> print annot2
