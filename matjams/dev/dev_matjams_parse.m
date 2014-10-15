function jam_data = matjams_parse(jams_file)
%matjams_parse Parse a jams file into a more sane data structure.
%   Returns a struct with annotation types as fields.
%
% SYNOPSIS
%
%   jam_data = matjams_parse(filename)
%

jams_struct = matjams_read(jams_file);


beat = get_data(jams_struct,'beat');
chord = get_data(jams_struct,'chord');
genre = get_data(jams_struct, 'genre');
key = get_data(jams_struct, 'key');
melody = get_data(jams_struct, 'melody');
mood = get_data(jams_struct, 'mood');
note = get_data(jams_struct,'note');
onset = get_data(jams_struct, 'onset');
pattern = get_data(jams_struct, 'pattern');
pitch = get_data(jams_struct, 'pitch');
segment = get_data(jams_struct, 'segment');
source = get_data(jams_struct, 'source');
tag = get_data(jams_struct, 'tag');

metadata = jams_struct.file_metadata;

if isfield(jams_struct, 'sandbox')
    sandbox = jams_struct.sandbox;
else
    sandbox = [];
end

jam_data = struct;

jam_data.beats = beat;
jam_data.chords = chord;
jam_data.genre = genre;
jam_data.key = key;
jam_data.melody = melody;
jam_data.mood = mood;
jam_data.note = note;
jam_data.onset = onset;
jam_data.pattern = pattern;
jam_data.pitch = pitch;
jam_data.segment = segment;
jam_data.source = source;
jam_data.tag = tag;

jam_data.metadata = metadata;
jam_data.sandbox = sandbox;


%% Parsing Function %%

    function annot_data = get_data(jams_struct,annotation_type)
        % If field is not in the jams file, skip it %
        if ~isfield(jams_struct, annotation_type)
            annot_data = [];

        else
            annot_data = cell2mat(jams_struct.(annotation_type));
            n = size(annot_data,2);
            for i=1:n
                annot_data(i).data = cell2mat(annot_data(i).data);
            end
        end
    end

end