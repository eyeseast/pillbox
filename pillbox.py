"""
Python wrapper for NIH's Pillbox API.

Parameters:
    key - Security key required for API access
    shape - FDA SPL code for shape of pill (see definition below)
    color - FDA SPL code for color of pill (see definition below)
    score - Numeric value for FDA score value for pill
    size - Numeric value (whole number) for size in mm of pill. Search +/- 2 mm
    ingredient - Name of active ingredient.  Currently only one ingredient may be searched in each call.  There is currently no spellchecker.
    prodcode - FDA 9-digit Product Code in dashed format
    has_image - If 0, no image. If 1, image exists.
    
"""
import urllib, urllib2
import xml.etree.cElementTree as etree
from decimal import Decimal

BASE_URL = "http://pillbox.nlm.nih.gov/PHP/pillboxAPIService.php?"

SHAPES = {
    'BULLET': 'C48335',
    'CAPSULE': 'C48336',
    'CLOVER': 'C48337',
    'DIAMOND': 'C48338',
    'DOUBLE_CIRCLE': 'C48339',
    'FREEFORM': 'C48340',
    'GEAR': 'C48341',
    'HEPTAGON': 'C48342',
    'HEXAGON': 'C48343',
    'OCTAGON': 'C48344',
    'OVAL': 'C48345',
    'PENTAGON': 'C48346',
    'RECTANGLE': 'C48347',
    'ROUND': 'C48348',
    'SEMI_CIRCLE': 'C48349',
    'SQUARE': 'C48350',
    'TEAR': 'C48351',
    'TRAPEZOID': 'C48352',
    'TRIANGLE': 'C48353',
}

SHAPE_CODES = {
    'C48335': 'BULLET',
    'C48336': 'CAPSULE',
    'C48337': 'CLOVER',
    'C48338': 'DIAMOND',
    'C48339': 'DOUBLE_CIRCLE',
    'C48340': 'FREEFORM',
    'C48341': 'GEAR',
    'C48342': 'HEPTAGON',
    'C48343': 'HEXAGON',
    'C48344': 'OCTAGON',
    'C48345': 'OVAL',
    'C48346': 'PENTAGON',
    'C48347': 'RECTANGLE',
    'C48348': 'ROUND',
    'C48349': 'SEMI_CIRCLE',
    'C48350': 'SQUARE',
    'C48351': 'TEAR',
    'C48352': 'TRAPEZOID',
    'C48353': 'TRIANGLE'
}


COLORS = {
    'BLACK': 'C48323',
    'BLUE': 'C48333',
    'BROWN': 'C48332',
    'GRAY': 'C48324',
    'GREEN': 'C48329',
    'ORANGE': 'C48331',
    'PINK': 'C48328',
    'PURPLE': 'C48327',
    'RED': 'C48326',
    'TURQUOISE': 'C48334',
    'WHITE': 'C48325',
    'YELLOW': 'C48330',
}

COLOR_CODES = {
    'C48323': 'BLACK',
    'C48324': 'GRAY',
    'C48325': 'WHITE',
    'C48326': 'RED',
    'C48327': 'PURPLE',
    'C48328': 'PINK',
    'C48329': 'GREEN',
    'C48330': 'YELLOW',
    'C48331': 'ORANGE',
    'C48332': 'BROWN',
    'C48333': 'BLUE',
    'C48334': 'TURQUOISE'
}

IMAGE_SIZES = {
    'super_small': 'ss', # 91 x 65 png
    'small': 'sm',       # 161 x 115 jpg
    'medium': 'md',      # 448 x 320 jpg
    'large': 'lg'        # 840 x 600 jpg
}


class PillboxError(Exception):
    pass


class Pill(object):
    "Storage class for pills returned by Pillbox"
    
    def __init__(self, d):
        self.__dict__ = d
    
    # properties
    color        = property(lambda self: COLOR_CODES[self.SPLCOLOR])
    description  = property(lambda self: self.RXSTRING)
    has_image    = property(lambda self: bool(self.HAS_IMAGE))
    imprint      = property(lambda self: self.SPLIMPRINT)
    ingredients  = property(lambda self: self.INGREDIENTS.split('; '))
    product_code = property(lambda self: self.PRODUCT_CODE)
    rxcui        = property(lambda self: self.RXCUI)
    rxtty        = property(lambda self: self.RXTTY)
    score        = property(lambda self: int(self.SPLSCORE))
    set_id       = property(lambda self: self.SETID)
    shape        = property(lambda self: SHAPE_CODES[self.SPLSHAPE])
    size         = property(lambda self: Decimal(self.SPLSIZE))
    spl_id       = property(lambda self: self.SPL_ID)
    
    
    def image(self, size='small'):
        if not self.image_id:
            return ""
        
        IMAGE_URL = "http://pillbox.nlm.nih.gov/assets/%(size)s/%(image_id)s%(size_short)s.%(ext)s"
        if size == "super_small":
            ext = "png"
        else:
            ext = "jpg"
        
        return IMAGE_URL % {
            'size': size,
            'image_id': self.image_id,
            'size_short': IMAGE_SIZES[size],
            'ext': ext
        }
    
    
    def __str__(self):
        return self.description
    
    def __repr__(self):
        return "<Pill: %s>" % self.__str__()


class Pillbox(object):
    "Python client for NIH's Pillbox"
    
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def _apicall(self, **params):
        response = urllib2.urlopen(BASE_URL + urllib.urlencode(params)).read()
        if response == "No records found":
            return response

        try:
            pills = etree.fromstring(response)
            
        except Exception, e:
            raise PillboxError(e)
        
        return list(self._handle_pills(pills))
            
    
    def _handle_pills(self, pills):
        for pill in pills.findall('pill'):
            d = dict([
                (p.tag, p.text) for p in pill.getchildren()
            ])
            pill = Pill(d)
            yield pill

    
    def search(self, **params):
        params['key'] = self.api_key
        
        color = None
        if 'color' in params:
            if params['color'] in COLORS.values():
                color = params['color'] # if you want to use the color code, that's cool
            else:
                color = COLORS[params['color'].upper()]
        
        if color:
            params['color'] = color
        
        shape = None
        if 'shape' in params:
            if params['shape'] in SHAPES.values():
                shape = params['shape']
            else:
                shape = SHAPES[params['shape'].upper()]
        
        if shape:
            params['shape'] = shape
            
        return self._apicall(**params)



