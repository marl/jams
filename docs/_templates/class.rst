{{ fullname }}
{{ underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
    :members:
    :no-inherited-members:
    :show-inheritance:

    .. automethod:: __init__

    {% block attributes %}
    {% if attributes %}
    .. rubric:: Attributes

    .. autosummary::
    {% for item in attributes %}
       ~{{ name }}.{{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}

    {% block methods %}
    .. rubric:: Methods

    .. autosummary::
    {% for item in methods %}
       ~{{ name }}.{{ item }}
    {%- endfor %}
    {% endblock %}

