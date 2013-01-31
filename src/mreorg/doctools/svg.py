



from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree as ET
import os

import xml
import xmlwitch

import collections

def normalise_measurement(length):
    # Return size in mm:
    try:
        pxs = float(length)
        length='%fpt'%(pxs * 0.8)
    except:
        pass

    if length.endswith('pt'):
        return float(length.replace('pt','')) * 0.035277778 * 10.
    if length.endswith('cm'):
        return float(length.replace('cm','')) * 10.

    assert False, "unable to read length: %s" % length

def getWidthHeight(filename):
    root = ET.parse(filename).getroot()
    height = normalise_measurement( root.attrib['height'])
    width =  normalise_measurement( root.attrib['width'])

    height, width = int(height), int(width)
    #print height, width
    return width,height







class MyXMLParser(xml.sax.handler.ContentHandler):
    
    
    def get_style_dict(self, attrs):
        toks = [tok.split(':') for tok in attrs.get('style','').split(';') if tok]
        return  dict( toks )
        
    def update_global_style_dict(self, style_dict, element ):
        for k,v in style_dict.items():
            self.all_styles[element][k].add(v)
    
    
    def do_path(self, attrs):
        print 'Path!'
        
        
        style_dict = self.get_style_dict(attrs)
        self.update_global_style_dict(style_dict=style_dict, element='path')
        
        #print toks
        
        
        
        #print style_dict
        #stroke-width:1pt
        #self.colors
        
        
        
    def do_g(self, attrs):        
        pass
            
    def do_marker(self, attrs):
        pass
        #print 'marker'
        
        
    def do_tspan(self, attrs):
        pass
        #print 'tspan!'
    def do_text(self, attrs):
        #print 'Text!'
        pass

        
    def do_svg(self, attrs):        
        pass            
    def do_image(self, attrs):
        pass
        #print 'image!'
    
    
    
    def startElement(self, name, attrs):
        
        if 'transform' in attrs.keys():
            print name, attrs['transform']
        
        self.parse_stack.append( [] )
        
        # Sanity check:
        colored_properties = ['fill', 'stroke', 'stop-color', 'flood-color','lighting-color']
        assert len( set(attrs.keys()) & set(colored_properties) ) == 0, 'Unexpected properties'
        
        
        # Ignored elements:
        ignored_elements = ['defs', 'sodipodi:namedview', 'metadata',
                            'rdf:RDF', 'cc:Work', 'dc:format',
                            'dc:type', 'dc:title' ]
        
        method_lut = {
            'text': self.do_text,
            'g': self.do_g,
            'svg': self.do_svg,
            'text': self.do_text,
            'marker': self.do_marker,
            'tspan': self.do_tspan,
            'image': self.do_image,
            'text': self.do_text,
            'path': self.do_path,
            }
         
         
        if name in method_lut.keys():
            method_lut[name](attrs)
        elif name in ignored_elements:
            pass
        else:
            print 'Unknown node:', name
            assert False
        
        

    def endElement(self, name):
        self.parse_stack.pop()


    def __init__(self):
        self.colors = set()
        self.parse_stack=[]
        self.all_styles = collections.defaultdict( lambda : collections.defaultdict(set) )



class FileObj(object):
    def __init__(self, filename):
        self.filename = filename
    
    @property    
    def short_filename(self):
        return os.path.split( self.filename )[-1]
    @property
    def size_MB(self):
        return os.path.getsize(self.filename) / 1.0e6
        
    

class SVGFile(FileObj):
    def __init__(self, filename):
        super( SVGFile, self).__init__(filename=filename)
        
        
        with open(self.filename) as f:
            self.contents = f.read()
            
            
        # Load some details:
        self.x_mm = None
        self.y_mm = None

        self.internal_details = None

        self.parse_xml()
        
    
    def parse_xml(self):
        self.internal_details = MyXMLParser()
        xml.sax.parseString(self.contents, handler=self.internal_details)
        
        
    
    
        # Load some details:
        self.x_mm = 10
        self.y_mm = 10
    
        print self.internal_details.all_styles
        
    
    def __str__(self,):
        
        return '<SVGFile: [%3.2fMB]  %s  (%dx%d) >' % ( self.size_MB, self.short_filename, self.x_mm, self.y_mm)




    def build_html_details(self, xml=None, ):
        print 'details'
        
        if xml is None:
            xml = xmlwitch.Builder(version='1.0', encoding='utf-8')
            
            
        with xml.div():    
            with xml.h1():
                xml.write_escaped(self.filename)
            
            with xml.image(src=self.filename):
                pass
            
            #with xml.p():
            #    xml.write_escaped(str(self.internal_details.all_styles))
            
            #for each element type: g, path, text, etc
            for (element,attrs) in sorted(self.internal_details.all_styles.items()):
                with xml.table():
                    
                    # for each style type (color, fill, etc):
                    for (attr,vals) in sorted(attrs.items()):
                        
                        # Print each values
                        for i,val in enumerate(vals):
                            with xml.tr():
                                xml.td( element if i==0 else '' )
                                xml.td( attr )
                                xml.td(val)
            
        return  xml
            
            
        






