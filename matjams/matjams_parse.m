function [beats_mat, sections_mat, chords_mat, melody_mat, metadata] = ...
            matjams_parse(jams_struct)

%%%FOR TESTING ONLY%%%
if nargin == 0
    file = '/Users/rachelbittner/Dropbox/MARL/repos/jams/matjams/samples/ejh_20140224.json';
    jams_struct = matjams_read(file);
end
%%%%%%%%%%%%%%%%%%%%%%

beats_mat = get_beats(jams_struct);
sections_mat = get_sections(jams_struct);
chords_mat = get_chords(jams_struct);
melody_mat = get_melody(jams_struct);
metadata = get_metadata(jams_struct);


%% Parsing Functions %%
    function data_mat = get_beats(s)
        %TODO(rabitt)
        data_mat = None;
    end

    function data_mat = get_sections(s)
        %TODO(rabitt)
        data_mat = None;
    end

    function data_mat = get_chords(s)
        %TODO(rabitt)
        data_mat = None;
    end

    function data_mat = get_melody(s)
        %TODO(rabitt)
        data_mat = None;
    end

    function data_mat = get_metadata(s)
        %TODO(rabitt)
        data_mat = None;
    end

end