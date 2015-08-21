Example: beat and tempo
-----------------------

This section demonstrates a complete use-case of JAMS for storing estimated annotations.
The example uses `librosa <https://bmcfee.github.io/librosa/>`_ to estimate global tempo 
and beat timings.

example.py
~~~~~~~~~~

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

        tempo_a = jams.Annotation(namespace='tempo')
        tempo_a.annotation_metadata = jams.AnnotationMetadata(data_source='librosa tempo estimator')

        # Add beat timings to the annotation record.
        # The beat namespace does not require value or confidence fields,
        # so we can leave those blank.
        for t in beat_times:
            beat_a.append(time=t, duration=0.0)

        # Add tempo estimation to the annotation.
        # The tempo estimate is global, so it should start at time=0 and cover the full
        # track duration.
        # If we had a likelihood score on the estimation, it could be stored in 
        # `confidence`.  Since we have no competing estimates, we'll set it to 1.0.
        tempo_a.append(time=0.0,
                       duration=track_duration,
                       value=tempo,
                       confidence=1.0)

        # Store the new annotations in the jam
        jam.annotations.append(beat_a)
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
