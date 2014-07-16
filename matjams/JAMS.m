classdef JAMS

    % static methods
    methods(Static = true)
        
        % get jams data from json file
        function jams = load(filepath)
            jams = json.read(filepath);
        end
        
        % save data in jams object to json file
        function save(jam,filepath)
            json.write(jam,filepath);
        end
        
        function append(jam,filepath,new_filepath,on_conflict)
            if nargin < 4
                on_conflict = 'fail';
            end
            if nargin < 3
                new_filepath = filepath;
            end
            
            old_jam = load(filepath);
            display('**** UNIMPLEMENTED ****');
        end
    end
    
end