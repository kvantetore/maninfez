#!/usr/bin/env python

import webapp2
import urllib2
from lxml import etree


class PhotosHandler(webapp2.RequestHandler):
    def get(self):
        url = "https://picasaweb.google.com/data/feed/base/user/108332870494884223135/albumid/5628369433865741249?alt=kml&kind=photo&hl=no"
        req = urllib2.urlopen(url)
        tree = etree.parse(req)

        ns = dict(k="http://www.opengis.net/kml/2.2")
        elems = tree.findall("//k:IconStyle/k:scale", namespaces=ns)
        for e in elems:
            if e.text == "0.7":
                e.text = "1.0"

        self.response.headers["Content-Type"] = "application/vnd.google-earth.kml+xml"
        self.response.write(etree.tostring(tree))


app = webapp2.WSGIApplication([
    ('/photos', PhotosHandler)
], debug=True)
