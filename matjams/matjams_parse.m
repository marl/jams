function [beats, sections, notes, chords, melody, metadata] = ...
            matjams_parse(jams_file)

%%%FOR TESTING ONLY%%%
% if nargin == 0
%     file = '/Users/rachelbittner/Dropbox/MARL/repos/jams/matjams/samples/ejh_20140224.json';
%     jams_struct = matjams_read(file);
% end
%%%%%%%%%%%%%%%%%%%%%%

jams_struct = matjams_read(jams_file);

beats = get_data(jams_struct,'beat');
sections = [];
notes = get_data(jams_struct,'note');
chords = get_data(jams_struct,'chord');
melody = [];
metadata = jams_struct.file_metadata;

% beats = get_beats(jams_struct);
% sections = get_sections(jams_struct);
% notes = get_notes(jams_struct);
% chords = get_chords(jams_struct);
% melody = get_melody(jams_struct);
% metadata = get_metadata(jams_struct);


%% Parsing Functions %%
    function annot_data = get_data(jams_struct,annotation_type)
        annot_data = cell2mat(jams_struct.(annotation_type));
        n = size(annot_data,2);
        for i=1:n
            annot_data(i).data = cell2mat(annot_data(i).data);
        end
    end

    function data_mat = get_beats(s)
        data_mat = [];
    end

    function data_mat = get_sections(s)
        %TODO(rabitt)
        data_mat = [];
    end

    function data_mat = get_chords(s)
        %TODO(rabitt)
        data_mat = cell2mat(s.chord);
        data_mat = convert2mat(data_mat,'data');
%         n_annots = size(data_mat,2);
%         for i=1:n_annots
%             data_mat(i).data = cell2mat(data_mat(i).data);
%         end
        
    end

    function data_mat = get_melody(s)
        %TODO(rabitt)
        data_mat = [];
    end

    function data_mat = get_metadata(s)
        %TODO(rabitt)
        data_mat = [];
    end
end