#!/usr/bin/env python
#
# Copyright (C) 2011 Paulo Alcantara <pcacjr@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#

__author__ = """Paulo Alcantara (pcacjr@gmail.com)"""

import twitter

start_user = "pcacjr"

class Graph(object):
    def __init__(self):
        self.vertexes = {}

    def add_vertex(self, name, **kwargs):
        self.vertexes[name] = [kwargs, {"edges": {}}]

    def add_edge(self, v, *args, **kwargs):
        if not v in self.vertexes:
            self.add_vertex(v, color="white", dist=-1)

        for arg in args:
            if not arg in self.vertexes:
                self.add_vertex(arg, **kwargs)
                self.vertexes[arg][1]["edges"][v] = [kwargs, {"edges": {}}]

            self.vertexes[v][1]["edges"][arg] = [kwargs, {"edges": {}}]

    def __str__(self):
        s = ""
        for key, attrs in self.vertexes.iteritems():
            s += "Vertex: %s {\n\t" % key
            s += "Color: " + attrs[0]["color"] + ",\n\t"
            s += "Distance: " + str(attrs[0]["dist"]) + ",\n\t"
            s += "Edges: { "
            for _key, _attrs in attrs[1]["edges"].iteritems():
                s += _key + ", "

            s += "NULL }\n}\n\n"

        return s

def main():
    api = twitter.Api(
        consumer_key="otvCUwLAQ6tDl2YivKLdg",
        consumer_secret="Qvh2GfSUAgFmLjQDj33QmbA5VhDEWksDbMTt9PynmHM",
        access_token_key="408975678-A5zimpeA2rTWNk82SRAUBJaEEHm4q7Rk007SX8p4",
        access_token_secret="YlnhhajieCX6BWRFHHGQk0eVZfqYh6lstri9zG7ZcGY")

    #users = api.GetFriends(user=start_user)
    #print([u.name for u in users])

    g = Graph()
    g.add_vertex("test", color="white", dist=-1)
    g.add_edge("test", "test2", "test3", color="white", dist=8)
    g.add_edge("test4", "test5", color="white", dist=-1)
    print(g)

if __name__ == "__main__":
    main()
