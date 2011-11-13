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

# -*- coding: ISO-8859-1 -*-

__author__ = """Paulo Alcantara (pcacjr@gmail.com)"""

import sys
import os
import twitter
import codecs

start_user = "pcacjr"

class Graph(object):
    def __init__(self):
        self.vertexes = {}
        self.vertexes_no = 0

    def add_vertex(self, name, **kwargs):
        self.vertexes[name] = [kwargs, {"edges": {}}]
        self.vertexes_no += 1

    def add_edge(self, v, *args, **kwargs):
        if not v in self.vertexes:
            self.add_vertex(v, color="white", dist=-1)

        for arg in args:
            if not arg in self.vertexes:
                self.add_vertex(arg, **kwargs)
                color = self.vertexes[v][0]
                dist = self.vertexes[v][1]
                self.vertexes[arg][1]["edges"][v] = \
                            [color, dist, {"edges": {}}]

            self.vertexes[v][1]["edges"][arg] = [kwargs, {"edges": {}}]

    def del_vertex(self, name):
        del self.vertexes[name]

        keys = []
        for key, attrs in self.vertexes.iteritems():
            for _key, _attrs in attrs[1]["edges"].iteritems():
                if _key == name:
                    keys.append([key, _key])

        for k in keys:
            del self.vertexes[k[0]][1]["edges"][k[1]]

    def __get_right_graphviz_syntax(self, color):
        s = ""
        if color == "black":
            s += "[fontsize=8, fontcolor=\"white\", style=filled, fillcolor=\"black\"]"
        else:
            s += "[fontsize=8, style=filled, fillcolor=" + "\"" + color + \
                "\"" + "]"

        return s

    def draw(self, out_file):
        s = "strict graph G {\n\t"
        for key, attrs in self.vertexes.iteritems():
            s += "\"" + key + "\"" + " " + \
                self.__get_right_graphviz_syntax(attrs[0]["color"]) + \
                ";\n\t" + "\"" + key + "\"" + " -- {"

            if not attrs[1]["edges"]:
                continue

            for _key, _attrs in attrs[1]["edges"].iteritems():
                exists = "\"" + _key + "\"" + " --"
                if s.find(exists) != -1:
                    continue

                s += "\"" + _key + "\"" + " " + \
                    self.__get_right_graphviz_syntax(_attrs[0]["color"]) + " "

            s += "};\n\t"

        s += "}\n"

        f = codecs.open('.foobar.dot', 'wa', 'ISO-8859-15', 'replace')
        #f = open(".foobar.dot", "wa")
        f.write(s)
        f.close()

        s = "dot -T png .foobar.dot -o " + out_file + " -Gcharset=latin1"
        os.system(s)

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

"""The beautiful thing goes here man! :-)
"""
def bfs(api, g, s, e):
    users = api.GetFriends(user=start_user)
    queue = []

    try:
        if not s in [u.name for u in users]:
            raise Exception(s)
    except Exception as inst:
        print("Could not find user: ." % inst.args[0])
        return

    g.add_vertex(s, color="gray", dist=0)
    queue.append([s, users[[u.name for u in users].index(s)].screen_name])

    while queue:
        first = queue.pop()

        print("Person: %s" % first[0])
        try:
            #users = api.GetFriends(user=users[i].screen_name)
            users = api.GetFriends(user=first[1])
        except twitter.TwitterError, error:
            if g.vertexes[first[0]][0]["color"] == "black":
                print("Warning: you're removing a black vertex.")

            g.del_vertex(first[0])
            continue

        for u in users:
            if not u.name in g.vertexes:
                g.add_edge(first[0], u.name, color="white", dist=-1)

            if g.vertexes[u.name][0]["color"] == "white":
                g.vertexes[u.name][0]["color"] = "gray"
                dist = g.vertexes[first[0]][0]["dist"] + 1
                g.vertexes[u.name][0]["dist"] = dist
                queue.append([u.name, u.screen_name])

                if u.name == e:
                    g.vertexes[u.name][0]["color"] = "yellow"
                    return

        g.vertexes[first[0]][0]["color"] = "black"

def main():
    if not os.environ["CONSUMER_KEY"] or \
        not os.environ["CONSUMER_SECRET"] or \
        not os.environ["ACCESS_TOKEN_KEY"] or \
        not os.environ["ACCESS_TOKEN_SECRET"]:
        print("There is any missing environment variable that was not set.")
        sys.exit(-1)

    api = twitter.Api(
        consumer_key=os.environ["CONSUMER_KEY"],
        consumer_secret=os.environ["CONSUMER_SECRET"],
        access_token_key=os.environ["CONSUMER_SECRET"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"])

    g = Graph()

    #bfs(api, g, "Ricardo Salveti", "Lady Gaga")
    bfs(api, g, "Ricardo Salveti", "Energy Sports Brasil")
    g.draw("file.png")
    #bfs(api, g, "Ricardo Salveti", "Paulo Alcantara")
    #print(g)

    #g.add_vertex("test", color="white", dist=-1)
    #g.add_edge("test", "test2", "test3", "fuck", color="green", dist=8)
    #g.add_edge("test4", "test5", color="white", dist=-1)
    #g.del_vertex("test3")
    g.draw("file.png")
    #print(g)

if __name__ == "__main__":
    main()
