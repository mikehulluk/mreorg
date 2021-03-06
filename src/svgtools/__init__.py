#!/usr/bin/python
# -*- coding: utf-8 -*-

# svgutils.py
from lxml import etree
import svgutils.transform as sg
import collections

cm_to_pt = 28.346456693
#The spec says 1pt is 1.25px, 
def add_file_mpl(fig, filename, x_cm, y_cm,):
    return add_file(fig, filename, x_cm, y_cm, scale= 1.25)

def add_file(fig, filename, x_cm, y_cm, scale=1.0):
    figSub = sg.fromfile(filename)
    plSub = figSub.getroot()
    plSub.moveto(x_cm * cm_to_pt, y_cm * cm_to_pt, scale=scale)
    fig.append(plSub)

def add_text(fig,  text, x_cm, y_cm, size=12, weight='bold', rotate=None, textalign=None, style=None, **kwargs):

    x_pt = x_cm*cm_to_pt
    y_pt = y_cm*cm_to_pt

    #if rotate is not None:
    #    kwargs['transform'] = 'rotate(%f,%f,%f)' %(rotate, x_pt, y_pt)

    #if textalign is not None:
    #    kwargs['text-anchor'] = textalign

    if style is not None:
        kwargs['style'] = style


    if 'style' in kwargs:
        del kwargs['style']


    txt1 = sg.TextElement(x_pt,y_pt, text, size=size, weight=weight, **kwargs)
    fig.append(txt1)


def add_path(fig, pts, style=None):


    p = sg.PathElement(pts=pts, style=style)
    fig.append(p)


def define_marker(fig, marker_name, marker_dict, path_dict):

        m = sg.MarkerElement(marker_name, marker_dict, path_dict)

        defs = etree.Element('defs',)
        defs.append(m.root)
        fig.root.append(defs)

        return m


MarkerData = collections.namedtuple('MarkerData', "marker_dict path_dict")


def define_marker_std(fig, marker_name):
     std_markers = {
        'Arrow1Mend': MarkerData(
                        path_dict = { 'd':"M 0.0,0.0 L 5.0,-5.0 L -12.5,0.0 L 5.0,5.0 L 0.0,0.0 z ",
                                  'style':"fill-rule:evenodd;stroke:#000000;stroke-width:1.0pt;",
                                  'transform':"scale(0.4) rotate(180) translate(10,0)"},
                        marker_dict = {'orient':"auto",
                        'refY':"0.0",
                        'refX':"0.0",
                        'id':'Arrow1Mend',
                        'style':"overflow:visible;"} ),
                    }

     marker_data = std_markers[marker_name]
     define_marker( fig=fig,
                    marker_name=marker_name,
                    marker_dict=marker_data.marker_dict,
                    path_dict=marker_data.path_dict,
                    )

    


def add_figlabel(fig,  text, x_cm, y_cm, size=12, weight='bold', rotate=None, textalign=None, style=None, font=None, **kwargs):
    # Keep trailing '.'
    if text.endswith('.'):
        text = text[:-1]
    #text = text + '.'

    x_pt = x_cm * cm_to_pt
    y_pt = y_cm * cm_to_pt

    if rotate is not None:
        kwargs['transform'] = 'rotate(%f,%f,%f)' % (rotate, x_pt, y_pt)

    if textalign is not None:
        kwargs['text-anchor'] = textalign

    if style is not None:
        kwargs['style'] = style

    if font is None:
        font = 'Arial'

    txt1 = sg.TextElement(x_pt,y_pt, text, size=size, weight=weight, font=font, **kwargs)
    fig.append(txt1)





def write_rect_to_file(filename, x_cm, y_cm):
    data_dct = {'x_cm': x_cm, 'y_cm': y_cm}

    xml = r"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:cc="http://creativecommons.org/ns#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:svg="http://www.w3.org/2000/svg"
    xmlns="http://www.w3.org/2000/svg"
    version="1.1"
    width="%(x_cm)scm"
    height="%(y_cm)scm"
    id="svg2">
    <defs id="defs4" />
    <g
       transform="translate(0.76087953,-0.17277988)"
       id="layer1">
       <rect
           width="%(x_cm)scm"
           height="%(y_cm)scm"
           x="0.05cm"
           y="0.05cm"
           id="rect2985"
           style="color:#000000;fill:#dfdfdf;fill-opacity:1;fill-rule:nonzero;stroke:#000000;stroke-width:1.51334381;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0;marker:none;visibility:visible;display:inline;overflow:visible;enable-background:accumulate" />

      </g>
    </svg>
    """ % data_dct

    with open(filename,'w') as fobj:
        fobj.write(xml)
    return filename


def figure_with_background(width_cm, height_cm):
    fig = sg.SVGFigure('%fcm' % width_cm, '%fcm' % height_cm)
    return fig


class StdLayout:

    COL0_TEXT = 0.5
    COL0_FIG = 0.75
    COL1_TEXT = 5.5
    COL1_FIG = 5.75

    ROW0_TEXT = 0.5
    ROW0_FIG = 0.0


