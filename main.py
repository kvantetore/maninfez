#!/usr/bin/env python

import webapp2
import urllib2
import json
import jinja2
import os
from lxml import etree


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])


class MapHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template("templates/map.html")
        self.response.write(template.render({}))


class PhotosHandler(webapp2.RequestHandler):
    def get(self):
        #load picasaweb gdata json
        url = "https://picasaweb.google.com/data/feed/base/user/108332870494884223135/albumid/5628369433865741249?alt=json&kind=photo&hl=no"
        req = urllib2.urlopen(url)
        tree = json.load(req)

        #create simplified json
        photos = []
        entries = tree["feed"]["entry"]
        for entry in entries:
            #skip entries without position
            if not "georss$where" in entry:
                continue

            #create simplified json for photo
            lat, lon = entry["georss$where"]["gml$Point"]["gml$pos"]["$t"].split(" ")
            new_entry = {
                "category": entry["category"],
                "title": entry["title"]["$t"],
                "date": entry["updated"]["$t"],
                "thumbnail": entry["media$group"]["media$thumbnail"][0],
                "photo": entry["media$group"]["media$thumbnail"][-1],
                "link": [l["href"] for l in entry["link"] if l["rel"] == "http://schemas.google.com/photos/2007#canonical"][0],
                "position": {
                    "lat": lat,
                    "lon": lon,
                },
            }
            photos.append(new_entry)
            #print json.dumps(new_entry, indent=4)

        self.response.headers["Content-Type"] = "text/json"
        self.response.headers["Access-Control-Allow-Origin"] = "*"
        self.response.write(json.dumps({
            "photos": photos
        }, indent=4))


class OldPhotosHandler(webapp2.RequestHandler):
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
    ("/", MapHandler),
    ('/photos', OldPhotosHandler),
    ('/photos/json', PhotosHandler),
], debug=True)
