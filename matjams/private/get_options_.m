function options = get_options_(options, varargin)
%GET_OPTIONS_ Get options from an argument list.
  assert(isstruct(options) && isscalar(options));
  option_names = fieldnames(options);
  for i = 1:2:numel(varargin)
    index = strcmpi(varargin{i}, option_names);
    if any(index)
      option_name = option_names{index};
      options.(option_name) = feval(class(options.(option_name)), ...
                                    varargin{i+1});
    else
      error('Unknown option `%s`.', varargin{i});
    end
  end
end