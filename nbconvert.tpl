{%- extends 'classic/index.html.j2' -%}

{# This template will render cells with tags highlight,
highlight_red and hide_code differently 
- also fixes summary-details arrow not showing in exported HTML
- created from files in:
    https://github.com/ipython-contrib/jupyter_contrib_nbextensions/tree/master/src/jupyter_contrib_nbextensions/templates
    https://github.com/ipython-contrib/jupyter_contrib_nbextensions/tree/master/src/jupyter_contrib_nbextensions/nbextensions/toc2
    
    https://github.com/ipython-contrib/jupyter_contrib_nbextensions/blob/master/src/jupyter_contrib_nbextensions/templates/toc2.tpl
    https://github.com/ipython-contrib/jupyter_contrib_nbextensions/tree/master/src/jupyter_contrib_nbextensions/nbextensions/toc2
#}

{%- block header -%}

{{ super() }}

{%- endblock header -%}

{% block input_group -%}
{%- if cell.metadata.hide_input or nb.metadata.hide_input -%}
{%- else -%}
    {% if 'highlight_red' in cell['metadata'].get('tags', []) %}
        <div style="background-color:#FFF0F2">
            {{ super() }}
        </div>
    {% elif 'highlight' in cell['metadata'].get('tags', []) %}
        <div style="background-color:#E0F0F5">
            {{ super() }}
        </div>
    {% elif 'tud_corporate' in cell['metadata'].get('tags', []) %}
        <div style="background-color: #00305D">
            {{ super() }}
        </div>
    {% else %}
        {% if 'hide_code' in cell['metadata'].get('tags', []) %}
            <div style="padding-left: 40px; font-size: 20px;">•••</div>
        {% else %}
            {{ super() }}
        {% endif %}
    {% endif %}
{%- endif -%}
{% endblock input_group %}
    
{% block output_group -%}
{%- if cell.metadata.hide_output -%}
{%- else -%}
    {{ super() }}
{%- endif -%}
{% endblock output_group %}

{%- block rawcell -%}
    <div class="cell border-box-sizing text_cell rendered">
        <div class="prompt"> </div>
        <div class="inner_cell highlight" style="margin:5px; padding: 10px; color: grey; border-width: 0.25px; border-color: lightgrey;">{{ super() }}</div>
    </div>
{%- endblock rawcell -%}

{% block output_area_prompt %}
{%- if cell.metadata.hide_input or nb.metadata.hide_input -%}
    <div class="prompt"> </div>
{%- else -%}
    {{ super() }}
{%- endif -%}
{% endblock output_area_prompt %}

{%- block html_head_js -%}
{%- block html_head_js_requirejs -%}
<script src="{{ resources.require_js_url }}"></script>
{%- endblock html_head_js_requirejs -%}
{%- block html_head_js_jquery -%}
<script src="{{ resources.jquery_url }}"></script>
{%- endblock html_head_js_jquery -%}
{%- endblock html_head_js -%}

{%- block html_head -%}

{{ super() }}

{% for css in resources.inliner.css -%}
    <style type="text/css">
    {{ css }}
    </style>
{% endfor %}

{% for js in resources.inliner.js -%}
    <script type="text/javascript">
    {{ js }}
    </script>
{% endfor %}

    <link  rel="stylesheet" type="text/css" href="https://ad.vgiscience.org/cdn/jquery/jquery-ui.css">
    
    <link rel="stylesheet" type="text/css" href="https://ad.vgiscience.org/cdn/toc2/main_v2.css">
    
    <link rel="stylesheet" type="text/css" href="https://ad.vgiscience.org/cdn/fontawesome/font-awesome.min.css">

    <script type="text/javascript" src="https://ad.vgiscience.org/cdn/jquery/jquery-ui.min.js"></script>
    
    <script src="https://ad.vgiscience.org/cdn/toc2/toc2.js"></script>
    
    <script>
    $( document ).ready(function(){
            var cfg = {{ nb.get('metadata', {}).get('toc', {})|tojson|safe }};
            cfg.navigate_menu=false;
            // fire the main function with these parameters
            require(['nbextensions/toc2/toc2'], function (toc2) {
                toc2.table_of_contents(cfg);
            });
    });
    </script>
    
    <style type="text/css">
    /* Fix details summary arrow
       not shown in Firefox
       due to bootstrap
       display: block;
     */
    summary {
        display: list-item;
        outline: none;
    }
    /* Show Hand Cursor for details tags
     */
    details summary { 
        cursor: pointer;
    }
    body {
        background-color: #e9eaeb;
    }
    </style>
    
{%- endblock html_head -%}

{%- block footer -%}

<div style="text-align:center"><p><a style="font-size:1.0em;color:silver;text-decoration: none;" href="https://gitlab.hrz.tu-chemnitz.de/ioer/common/jupyter-base-template">IOER RDC Jupyter Base Template v0.10.0</a></p></div>

{{ super() }}

<footer style="width:100%; text-align:right; margin-top:10px">
<a href="https://www.ioer-fdz.de/"><img alt="IOER-FDZ-Logo" src="https://kartographie.geo.tu-dresden.de/ad/jupyter_python_datascience/FDZ-Logo_DE_RGB-blk_bg-tra_mgn-full_h200px_web.svg" style="position:relative;width:256px;margin-right:10px;clear: both;"></a>
<div class="slide-number impressum" style="display: block;display; min-height:50px; margin-left: auto; margin-right: 50px;">

                <a href="https://www.ioer.de/impressum">Impressum </a> |
                <a href="https://www.ioer.de/datenschutz">Datenschutz </a> |
                <a href="https://www.ioer.de/barrierefreiheit">Barrierefreiheit </a>
</div></footer>



{%- endblock footer -%}