matjams
=======

Matlab library for loading JAMS files.

Usage
-------------

To load a .jams file:
```
jam_data = JAMS.load(jam_filepath.jams)
```
The output `jam_data` will be a struct with the same tree-structure as the
original JAMS file. Converting this into a more Matlab-friendly format requires
unpacking.

For example, to access the data for a particular annotation task:
```
chord_data = jam_data.chords(1).data
n = size(chord_data, 2)
chord_array = cell(n, 3)
for i=1:n
    chord_array{i,1} = chord_data(i).start_t.value
    chord_array{i,2} = chord_data(i).end_t.value
    chord_array{i,2} = chord_data(i).label.value
end
```