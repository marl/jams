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
    tempo_a = jams.Annotation(namespace='tempo', time=0, duration=track_duration)
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
