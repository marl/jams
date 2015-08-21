Examples 
--------

Storing annotations
^^^^^^^^^^^^^^^^^^^

This section demonstrates a complete use-case of JAMS for storing estimated annotations.
The example uses `librosa <https://bmcfee.github.io/librosa/>`_ to estimate global tempo 
and beat timings.

example_beat.py
~~~~~~~~~~~~~~~

The following script loads the librosa example audio clip, estimates the track duration,
tempo, and beat timings, and constructs a JAMS object to store the estimations.

.. code-block:: python
    :linenos: 

    #!/usr/bin/env python

    import librosa
    import jams

    def beat_track(infile, outfile):

        # Load the audio file
        y, sr = librosa.load(infile)

        # Compute the track duration
        track_duration = librosa.get_duration(y=y, sr=sr)

        # Extract tempo and beat estimates
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

        # Convert beat frames to time
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        # Construct a new JAMS object and annotation records
        jam = jams.JAMS()

        # Store the track duration
        jam.file_metadata.duration = track_duration

        beat_a = jams.Annotation(namespace='beat')
        beat_a.annotation_metadata = jams.AnnotationMetadata(data_source='librosa beat tracker')

        # Add beat timings to the annotation record.
        # The beat namespace does not require value or confidence fields,
        # so we can leave those blank.
        for t in beat_times:
            beat_a.append(time=t, duration=0.0)

        # Store the new annotation in the jam
        jam.annotations.append(beat_a)

        # Add tempo estimation to the annotation.
        tempo_a = jams.Annotation(namespace='tempo')
        tempo_a.annotation_metadata = jams.AnnotationMetadata(data_source='librosa tempo estimator')

        # The tempo estimate is global, so it should start at time=0 and cover the full
        # track duration.
        # If we had a likelihood score on the estimation, it could be stored in 
        # `confidence`.  Since we have no competing estimates, we'll set it to 1.0.
        tempo_a.append(time=0.0,
                       duration=track_duration,
                       value=tempo,
                       confidence=1.0)

        # Store the new annotation in the jam
        jam.annotations.append(tempo_a)

        # Save to disk
        jam.save(outfile)


    if __name__ == '__main__':

        infile = librosa.util.example_audio_file()
        beat_track(infile, 'output.jams')



output.jams
~~~~~~~~~~~
The above script generates the following JAMS object.

.. code-block:: javascript
    :linenos:

    {
      "sandbox": {}, 
      "annotations": [
        {
          "data": [
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 7.430385
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 8.289524
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 9.218322
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 10.1239
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 11.145578
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 12.190476
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 13.212154
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 14.140952
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 15.27873
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 16.207528
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 17.113107
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 18.041905
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 18.970703
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 19.899501
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 20.805079
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 21.733878
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 22.662676
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 23.591474
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 24.497052
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 25.42585
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 26.354649
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 27.283447
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 28.189025
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 29.117823
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 30.069841
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 30.97542
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 31.880998
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 32.833016
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 33.738594
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 34.667392
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 35.572971
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 36.524989
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 37.453787
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 38.359365
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 39.264942
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 40.216961
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 41.14576
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 42.051338
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 42.956916
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 43.885714
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 44.837732
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 45.97551
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 46.904308
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 47.833107
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 48.761905
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 49.667483
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 50.596281
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 51.525078
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 52.453878
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 53.359456
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 54.288254
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 55.217052
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 56.12263
            }, 
            {
              "duration": 0.0, 
              "confidence": NaN, 
              "value": NaN, 
              "time": 57.051429
            }
          ], 
          "annotation_metadata": {
            "annotation_tools": "", 
            "curator": {
              "name": "", 
              "email": ""
            }, 
            "annotator": {}, 
            "version": "", 
            "corpus": "", 
            "annotation_rules": "", 
            "validation": "", 
            "data_source": "librosa beat tracker"
          }, 
          "namespace": "beat", 
          "sandbox": {}
        }, 
        {
          "data": [
            {
              "duration": 61.458866, 
              "confidence": 1.0, 
              "value": 64.599609375, 
              "time": 0.0
            }
          ], 
          "annotation_metadata": {
            "annotation_tools": "", 
            "curator": {
              "name": "", 
              "email": ""
            }, 
            "annotator": {}, 
            "version": "", 
            "corpus": "", 
            "annotation_rules": "", 
            "validation": "", 
            "data_source": "librosa tempo estimator"
          }, 
          "namespace": "tempo", 
          "sandbox": {}
        }
      ], 
      "file_metadata": {
        "jams_version": "0.2.0", 
        "title": "", 
        "identifiers": {}, 
        "release": "", 
        "duration": 61.45886621315193, 
        "artist": ""
      }
    }


Evaluating annotations
^^^^^^^^^^^^^^^^^^^^^^

The following script illustrates how to evaluate one JAMS annotation object against another using the
built-in `eval` submodule to wrap `mir_eval <https://craffel.github.io/mir_eval>`_.

Given two jams files, say, `reference.jams` and `estimate.jams`, the script first loads them as objects
(``j_ref`` and ``j_est``, respectively).  It then uses the :ref:`jams.JAMS.search` method to locate all
annotations of namespace ``"beat"``.  If no matching annotations are found, an empty list is returned.

In this example, we are assuming that each JAMS file contains only a
single annotation of interest, so the first result is taken by indexing the results at 0.  (In general, you
may want to use `annotation_metadata` to select a specific annotation from the JAMS object, if multiple are
present.)

Finally, the two annotations are compared by calling :ref:`jams.eval.beat`, which returns an ordered
dictionary of evaluation metrics for the annotations in question.

example_eval.py
~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:

    #!/usr/bin/env python

    import sys
    import jams

    from pprint import pprint

    def compare_beats(f_ref, f_est):

        # f_ref contains the reference annotations
        j_ref = jams.load(f_ref)

        # f_est contains the estimated annotations
        j_est = jams.load(f_est)

        # Get the first reference beats
        beat_ref = j_ref.search(namespace='beat')[0]
        beat_est = j_est.search(namespace='beat')[0]

        # Get the scores
        return jams.eval.beat(beat_ref, beat_est)


    if __name__ == '__main__':

        f_ref, f_est = sys.argv[1:]
        scores = compare_beats(f_ref, f_est)

        # Print them out
        pprint(dict(scores))


Data conversion
^^^^^^^^^^^^^^^

JAMS provides some basic functionality to help convert from flat file formats (e.g., CSV or LAB).

example_chord_import.py
~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python
    :linenos:

    #!/usr/bin/env python

    import jams
    import sys

    def import_chord_jams(infile, outfile):

        # import_lab returns a new jams object,
        # and a handle to the newly created annotation
        jam, chords = jams.util.import_lab('chord', infile)

        # Infer the track duration from the end of the last annotation
        duration = (chords.data['time'] + chords.data['duration']).max()

        # this timing will be in pandas timedelta.
        # calling duration.total_seconds() converts to float
        jam.file_metadata.duration = duration.total_seconds()

        # save to disk
        jam.save(outfile)


    if __name__ == '__main__':

        infile, outfile = sys.argv[1:]
        import_chord_jams(infile, outfile)

chord_output.jams
~~~~~~~~~~~~~~~~~

Calling the above script on `01_-_I_Saw_Her_Standing_There.lab
<http://isophonics.net/files/annotations/chordlab/The%20Beatles/01_-_Please_Please_Me/01_-_I_Saw_Her_Standing_There.lab>`_
from `IsoPhonics <http://isophonics.net/>`_ should produce the following JAMS object:

.. code-block:: javascript

    {
      "sandbox": {}, 
      "annotations": [
        {
          "data": [
            {
              "duration": 2.612267, 
              "confidence": 1.0, 
              "value": "N", 
              "time": 0.0
            }, 
            {
              "duration": 8.846803, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 2.612267
            }, 
            {
              "duration": 1.462857, 
              "confidence": 1.0, 
              "value": "A", 
              "time": 11.45907
            }, 
            {
              "duration": 4.521547, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 12.921927
            }, 
            {
              "duration": 2.966888, 
              "confidence": 1.0, 
              "value": "B", 
              "time": 17.443474
            }, 
            {
              "duration": 1.497687, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 20.410362
            }, 
            {
              "duration": 1.462858, 
              "confidence": 1.0, 
              "value": "E:7/3", 
              "time": 21.908049
            }, 
            {
              "duration": 1.486077, 
              "confidence": 1.0, 
              "value": "A", 
              "time": 23.370907
            }, 
            {
              "duration": 1.486077, 
              "confidence": 1.0, 
              "value": "A:min/b3", 
              "time": 24.856984
            }, 
            {
              "duration": 1.497687, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 26.343061
            }, 
            {
              "duration": 1.509297, 
              "confidence": 1.0, 
              "value": "B", 
              "time": 27.840748
            }, 
            {
              "duration": 5.955918, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 29.350045
            }, 
            {
              "duration": 1.497687, 
              "confidence": 1.0, 
              "value": "A", 
              "time": 35.305963
            }, 
            {
              "duration": 4.459452, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 36.80365
            }, 
            {
              "duration": 2.982544, 
              "confidence": 1.0, 
              "value": "B", 
              "time": 41.263102
            }, 
            {
              "duration": 1.474467, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 44.245646
            }, 
            {
              "duration": 1.486077, 
              "confidence": 1.0, 
              "value": "E:7/3", 
              "time": 45.720113
            }, 
            {
              "duration": 1.486077, 
              "confidence": 1.0, 
              "value": "A", 
              "time": 47.20619
            }, 
            {
              "duration": 1.462857, 
              "confidence": 1.0, 
              "value": "A:min/b3", 
              "time": 48.692267
            }, 
            {
              "duration": 1.497687, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 50.155124
            }, 
            {
              "duration": 1.486077, 
              "confidence": 1.0, 
              "value": "B", 
              "time": 51.652811
            }, 
            {
              "duration": 2.972155, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 53.138888
            }, 
            {
              "duration": 9.020952, 
              "confidence": 1.0, 
              "value": "A", 
              "time": 56.111043
            }, 
            {
              "duration": 3.018594, 
              "confidence": 1.0, 
              "value": "B", 
              "time": 65.131995
            }, 
            {
              "duration": 3.041814, 
              "confidence": 1.0, 
              "value": "A", 
              "time": 68.150589
            }, 
            {
              "duration": 3.006984, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 71.192403
            }, 
            {
              "duration": 1.497687, 
              "confidence": 1.0, 
              "value": "A", 
              "time": 74.199387
            }, 
            {
              "duration": 4.539501, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 75.697074
            }, 
            {
              "duration": 2.972155, 
              "confidence": 1.0, 
              "value": "B", 
              "time": 80.236575
            }, 
            {
              "duration": 3.012963, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 83.20873
            }, 
            {
              "duration": 1.514928, 
              "confidence": 1.0, 
              "value": "A", 
              "time": 86.221693
            }, 
            {
              "duration": 1.520907, 
              "confidence": 1.0, 
              "value": "A:min/b3", 
              "time": 87.736621
            }, 
            {
              "duration": 1.462857, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 89.257527
            }, 
            {
              "duration": 1.437068, 
              "confidence": 1.0, 
              "value": "B", 
              "time": 90.720385
            }, 
            {
              "duration": 11.949236, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 92.157453
            }, 
            {
              "duration": 3.018594, 
              "confidence": 1.0, 
              "value": "B", 
              "time": 104.106689
            }, 
            {
              "duration": 3.053424, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 107.125283
            }, 
            {
              "duration": 2.94538, 
              "confidence": 1.0, 
              "value": "A", 
              "time": 110.178707
            }, 
            {
              "duration": 1.489631, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 113.124087
            }, 
            {
              "duration": 1.486077, 
              "confidence": 1.0, 
              "value": "B", 
              "time": 114.613718
            }, 
            {
              "duration": 2.845166, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 116.099795
            }, 
            {
              "duration": 9.101501, 
              "confidence": 1.0, 
              "value": "A", 
              "time": 118.944961
            }, 
            {
              "duration": 3.006984, 
              "confidence": 1.0, 
              "value": "B", 
              "time": 128.046462
            }, 
            {
              "duration": 2.983764, 
              "confidence": 1.0, 
              "value": "A", 
              "time": 131.053446
            }, 
            {
              "duration": 3.006985, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 134.03721
            }, 
            {
              "duration": 1.431329, 
              "confidence": 1.0, 
              "value": "A", 
              "time": 137.044195
            }, 
            {
              "duration": 4.582639, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 138.475524
            }, 
            {
              "duration": 2.983764, 
              "confidence": 1.0, 
              "value": "B", 
              "time": 143.058163
            }, 
            {
              "duration": 1.509297, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 146.041927
            }, 
            {
              "duration": 1.509297, 
              "confidence": 1.0, 
              "value": "E:7/3", 
              "time": 147.551224
            }, 
            {
              "duration": 1.451247, 
              "confidence": 1.0, 
              "value": "A", 
              "time": 149.060521
            }, 
            {
              "duration": 1.509297, 
              "confidence": 1.0, 
              "value": "A:min/b3", 
              "time": 150.511768
            }, 
            {
              "duration": 1.509297, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 152.021065
            }, 
            {
              "duration": 1.532517, 
              "confidence": 1.0, 
              "value": "B", 
              "time": 153.530362
            }, 
            {
              "duration": 4.469842, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 155.062879
            }, 
            {
              "duration": 1.532517, 
              "confidence": 1.0, 
              "value": "B", 
              "time": 159.532721
            }, 
            {
              "duration": 4.516281, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 161.065238
            }, 
            {
              "duration": 1.532517, 
              "confidence": 1.0, 
              "value": "B", 
              "time": 165.581519
            }, 
            {
              "duration": 1.532517, 
              "confidence": 1.0, 
              "value": "A", 
              "time": 167.114036
            }, 
            {
              "duration": 1.090856, 
              "confidence": 1.0, 
              "value": "E", 
              "time": 168.646553
            }, 
            {
              "duration": 1.949764, 
              "confidence": 1.0, 
              "value": "E:9", 
              "time": 169.737409
            }, 
            {
              "duration": 4.116909, 
              "confidence": 1.0, 
              "value": "N", 
              "time": 171.687173
            }
          ], 
          "annotation_metadata": {
            "annotation_tools": "", 
            "curator": {
              "name": "", 
              "email": ""
            }, 
            "annotator": {}, 
            "version": "", 
            "corpus": "", 
            "annotation_rules": "", 
            "validation": "", 
            "data_source": ""
          }, 
          "namespace": "chord", 
          "sandbox": {}
        }
      ], 
      "file_metadata": {
        "jams_version": "0.2.0", 
        "title": "", 
        "identifiers": {}, 
        "release": "", 
        "duration": 175.804082, 
        "artist": ""
      }
    }


More examples
~~~~~~~~~~~~~
In general, converting a dataset to JAMS format will require a bit more work to ensure that value fields
conform to the specified namespace schema, but the import script above should serve as a simple starting
point.

For further reference, a separate repository `jams-data <https://github.com/marl/jams-data>`_ has been 
created to house conversion scripts for publicly available datasets.
Note that development of converters is a work in progress, so proceed with caution!
