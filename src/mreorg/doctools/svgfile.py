#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import collections
from functools import partial
import shutil


import xml.etree.ElementTree as ET
import xml
import xml.sax

try:
    import xmlwitch
except ImportError:
    print "Unable to import xmlwitch (needed to write XML/SVG files)"



def normalise_measurement(length):
    # Return size in mm:
    try:
        pxs = float(length)
        length = '%fpt' % (pxs * 0.8)
    except:
        pass

    if length.endswith('pt'):
        return float(length.replace('pt', '')) * 0.035277778 * 10.
    if length.endswith('cm'):
        return float(length.replace('cm', '')) * 10.

    assert False, 'unable to read length: %s' % length


def getWidthHeight(filename):
    root = ET.parse(filename).getroot()
    height = normalise_measurement(root.attrib['height'])
    width = normalise_measurement(root.attrib['width'])

    (height, width) = (int(height), int(width))
    return (width, height)


class MyXMLParser(xml.sax.handler.ContentHandler):

    def get_style_dict(self, attrs):
        toks = [tok.split(':') for tok in attrs.get('style','').split(';') if tok]
        return  dict( toks )

    def update_global_style_dict(self, style_dict, element):
        for (k, v) in style_dict.items():
            self.svg_data.all_styles[element][k].add(v)

    def do_path(self, attrs):
        style_dict = self.get_style_dict(attrs)
        self.update_global_style_dict(style_dict=style_dict, element='path')




    def do_text(self, attrs):
        style_dict = self.get_style_dict(attrs)
        self.update_global_style_dict(style_dict=style_dict, element='text')

    def do_g(self, attrs):
        pass

    def do_marker(self, attrs):
        pass

    def do_tspan(self, attrs):
        pass

    def do_svg(self, attrs):
        pass

    def do_image(self, attrs):
        pass

    def do_rect(self, attrs):
        pass
    def do_circle(self, attrs):
        pass
    def do_ellipse(self, attrs):
        pass
    def do_polygon(self, attrs):
        pass
    def do_polyline(self, attrs):
        pass
    def do_style(self, attrs):
        pass
    def do_line(self, attrs):
        pass


    def startElement(self, name, attrs):
        self.svg_data.n_nodes+=1

        if 'transform' in attrs.keys():
            tr = attrs['transform']
            if tr.startswith('rotate') or tr.startswith('translate'):
                pass
            else:
                self.svg_data.transforms.append(tr)
            #print name, attrs['transform']

        self.parse_stack.append( [] )

        # Sanity check:
        colored_properties = ['fill', 'stroke', 'stop-color', 'flood-color','lighting-color']
        if len( set(attrs.keys()) & set(colored_properties) ) != 0:
            print  'Unexpected properties'
            print 'Node', name, attrs.keys()


        # Ignored elements:
        ignored_elements = ['defs', 'sodipodi:namedview','sodipodi:guide', 'metadata',
                            'rdf:RDF', 'cc:Work', 'inkscape:grid',
                            'dc:format', 'dc:type', 'dc:title',
                            'mask','clipPath','radialGradient','stop','linearGradient','filter', 'feGaussianBlur',
                            'flowRoot', 'flowRegion','flowPara',
                            'use', ]

        method_lut = {
            'text': self.do_text,
            'rect': self.do_rect,
            'circle': self.do_circle,
            'ellipse': self.do_ellipse,
            'g': self.do_g,
            'svg': self.do_svg,
            'text': self.do_text,
            'marker': self.do_marker,
            'tspan': self.do_tspan,
            'style': self.do_style,
            'image': self.do_image,
            'text': self.do_text,
            'path': self.do_path,
            'line': self.do_line,
            'polyline': self.do_polyline,
            'polygon': self.do_polygon,
            }


        if name in method_lut.keys():
            method_lut[name](attrs)
        elif name in ignored_elements:
            pass
        else:
            print 'Unknown node:', name
            assert False



    def endElement(self, name):
        #self.parse_stack.pop()
        pass


    def __init__(self):

        self.svg_data = SVGData()
        self.parse_stack=[]


        #self.transforms=[]




class SVGData(object):
    def __init__(self):
        self.n_nodes = 0

        self.all_styles = collections.defaultdict( partial(collections.defaultdict,set ) )
        self.transforms = []

        # Load some details:
        self.x_mm = 10
        self.y_mm = 10




class FileObj(object):
    def __init__(self, filename):
        self.filename = filename

    @property
    def short_filename(self):
        return os.path.split( self.filename )[-1]
    @property
    def full_filename(self):
        return os.path.join( os.getcwd(), self.filename )

    @property
    def size_MB(self):
        return os.path.getsize(self.filename) / 1.0e6


import pickle

class SVGFile(FileObj):
    xml_parse_cache_filename='.xmlcache'

    @classmethod
    def load_parse_cache(cls,):
        if os.path.exists(cls.xml_parse_cache_filename):
            with open(cls.xml_parse_cache_filename) as f:
                parse_cache = pickle.load(f)
        else:
            parse_cache = {}
        return parse_cache

    @classmethod
    def save_parse_cache(cls,parse_cache):
        with open(cls.xml_parse_cache_filename,'w') as f:
            pickle.dump(parse_cache,f)


    def __init__(self, filename):
        super( SVGFile, self).__init__(filename=filename)


        with open(self.filename) as f:
            self.contents = f.read()

        print filename
        self.svg_data = self.parse_xml()

        print str(self)



    def parse_xml(self):

        parse_cache=self.load_parse_cache()
        if not self.filename in parse_cache:

            my_parser = MyXMLParser()
            xml.sax.parse(self.filename, handler=my_parser)
            parse_cache[self.filename] = my_parser.svg_data
            self.save_parse_cache(parse_cache)

        return parse_cache[self.filename]







    def __str__(self,):

        return '<SVGFile: [%3.2f MB; %4d nodes] %s (%dx%d) NTransforms: %s>' % (
                self.size_MB,
                self.svg_data.n_nodes,
                self.short_filename,
                self.svg_data.x_mm,
                self.svg_data.y_mm,
                len(self.svg_data.transforms) )




    def build_html_details(self, xml=None, ):

        if xml is None:
            xml = xmlwitch.Builder(version='1.0', encoding='utf-8')


        with xml.div():
            with xml.h1():
                with xml.a(name=self.short_filename):
                    #xml.write_escaped(self.filename)
                    xml.write_escaped(self.short_filename)

            with xml.image(src=self.full_filename):
                pass

            #for each element type: g, path, text, etc
            for (element,attrs) in sorted(self.svg_data.all_styles.items()):
                with xml.table():

                    # for each style type (color, fill, etc):
                    for (attr,vals) in sorted(attrs.items()):

                        # Print each values
                        for i,val in enumerate(vals):
                            with xml.tr():
                                xml.td( element if i==0 else '' )
                                xml.td( attr )
                                xml.td(val)

            xml.write_escaped( str(','.join(self.svg_data.transforms) ) )

        return  xml



#def format_

class SVGFileSet(object):
    def __init__(self, svgfiles):
        self.svgfiles = svgfiles


    def build_summary_table(self, xml):

        all_styles = collections.defaultdict( partial(collections.defaultdict, partial(collections.defaultdict,set ) ) )

        for svgfile in self.svgfiles:
            for (element, data) in svgfile.svg_data.all_styles.items():
                for (prop, values) in data.items():
                    for value in values:
                        all_styles[element][prop][value].add(svgfile)


        xml.h1('Summary')
        with xml.table():

            for element in sorted(all_styles):
                for prop in sorted(all_styles[element]):
                    for value in sorted(all_styles[element][prop]):

                        with xml.tr():

                            kwargs = {}
                            if value.startswith('#'):
                                kwargs['bgcolor'] = value

                            xml.td( element  )
                            xml.td( prop  )
                            xml.td( value, **kwargs )
                            svgfiles= sorted(all_styles[element][prop][value])
                            with xml.td():
                                xml.write( ','.join( ['<a href="#%s">%s</a>' % ( svgfile.short_filename, svgfile.short_filename) for svgfile in  svgfiles]) )


                        #for i,svgfile in enumerate(sorted(all_styles[element][prop][value])):
                        #        with xml.tr():

                        #            kwargs = {}
                        #            if value.startswith('#'):
                        #                kwargs['bgcolor'] = value

                        #            xml.td( element if i==0 else '' )
                        #            xml.td( prop if i==0 else '' )
                        #            xml.td( value if i==0 else '', **kwargs )
                        #            xml.td( svgfile.short_filename )



        #['node']['property'] -> ['file1','file2','file3'...]

        from matplotlib.colors import ColorConverter
        #pass
        #colors = set()

        import numpy as np
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        #from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')


        for element in sorted(all_styles):
            for prop in sorted(all_styles[element]):
                for value in sorted(all_styles[element][prop]):
                    if value.startswith('#'):
                        files = all_styles[element][prop][value]
                        s = float(len(files)) * 3

                        colors = np.array( ColorConverter().to_rgb(value) ) 
                        colors = colors.reshape( (1,3))
                        print colors
                        print colors.shape
                        l = ax.scatter(colors[:,0], colors[:,1], colors[:,2], c=colors, s=s, picker=5)
                        l.src_color = value
                        l.src_files = files





        def onpick(event):
            print 'On event', event, event.artist
            l = event.artist
            print l.src_color
            print [ f.filename for f in l.src_files]
        fig.canvas.mpl_connect('pick_event', onpick)

        plt.show()



    def build_html_output(self, output_dir='./image_html/'):

        xml = xmlwitch.Builder(version='1.0', encoding='utf-8')


        # Summary Table of all tags and colors:
        self.build_summary_table(xml)

        # Create the output:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # General table:
        for svgfile in sorted( self.svgfiles, key=lambda o:o.filename ):
            svgfile.build_html_details(xml=xml)

            # Copy files across:
            shutil.copyfile(svgfile.full_filename, os.path.join(output_dir,svgfile.short_filename ))



        with open(os.path.join(output_dir,'index.html'),'w' ) as f:
            f.write(str(xml))





