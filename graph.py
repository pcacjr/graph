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
from PySide import QtCore, QtGui
import re
import urllib2

image_path = "/home/pcacjr/src/other-graph/images/file.png"
loading_image_path = "/home/pcacjr/src/other-graph/images/loading.gif"
done_image_path = "/home/pcacjr/src/other-graph/images/done.gif"

class Graph(object):
    def __init__(self):
        self.vertexes = {}   # vertexes
        self.vertexes_no = 0 # number of vertexes in the graph

    """ Add a vertex to the graph.

        @name vertex's name
        @kwargs vertex's attributes
    """
    def add_vertex(self, name, **kwargs):
        """ add the new vertex to our dictionary (hash table) along
            with its attributes (@kwargs)
        """
        self.vertexes[name] = [kwargs, {"edges": {}}]
        # for each newly added vertex we increase our vertex count
        self.vertexes_no += 1

    """ Add an edge from @v (start vertex) to @args (other vertexes).

        @v start vertex
        @args one or more end vertexes
        @kwargs attributes of each other
    """
    def add_edge(self, v, *args, **kwargs):
        # if there isn't any @v vertex in the graph we add it to
        if not v in self.vertexes:
            self.add_vertex(v, color="white", dist=-1)

        # for each vertex passed in @args we add an edge from @v to
        for arg in args:
            if not arg in self.vertexes:
                """
                    arg isn't in the graph, so we add it to the graph
                    and then make an edge from @v to it
                """
                self.add_vertex(arg, **kwargs)
                color = self.vertexes[v][0]
                dist = self.vertexes[v][1]
                self.vertexes[arg][1]["edges"][v] = \
                            [color, dist, {"edges": {}}]

            self.vertexes[v][1]["edges"][arg] = [kwargs, {"edges": {}}]

    """ Delete a given vertex.

        @name vertex's name
    """
    def del_vertex(self, name):
        # delete the vertex of the graph
        del self.vertexes[name]

        """ Perhaps there must be vertexes which contain edges to the
            previously removed vertex. So we must remove this edge
            accordingly.
        """
        keys = []
        # iterate over the vertexes
        for key, attrs in self.vertexes.iteritems():
            for _key, _attrs in attrs[1]["edges"].iteritems():
                if _key == name:
                    """ Here we're storing pair of keys. One for the
                        vertex itself and the other a key within the
                        edges' dictionary.
                    """
                    keys.append([key, _key])

        # Now we probably have our pair of keys, so we do the trick...
        for k in keys:
            del self.vertexes[k[0]][1]["edges"][k[1]]

    """ Set attributes of a given vertex

        @v vertex's name
        @kwargs list of attributes
    """
    def set_attrs(self, v, **kwargs):
        # if there is no such vertex, just return
        if v not in self.vertexes:
            return

        # iterate over the vertexes
        for key, attrs in self.vertexes.iteritems():
            if key == v:
                # we got it! so let's set its attributes accordingly
                for k in kwargs:
                    attrs[0][k] = kwargs[k]

            """ Note: we can't forget the vertexes which do have it
                as adjacenct.
            """
            for _key, _attrs in attrs[1]["edges"].iteritems():
                if _key == v:
                    for k in kwargs:
                        _attrs[0][k] = kwargs[k]

    """ Given a color, return corresponding graphviz syntax for such
        color.

        @color vertex's color
    """
    def __get_right_graphviz_syntax(self, color):
        s = ""
        if color == "black":
            s += "[fontsize=8, fontcolor=\"white\", style=filled, fillcolor=\"black\"]"
        else:
            s += "[fontsize=8, style=filled, fillcolor=" + "\"" + color + \
                "\"" + "]"

        return s

    """ Draw a image from the built graph with the dot command.
        Note: we create a file that'll contain all graphviz syntaxes
              to draw our graph.

        @out_file output filename
    """
    def draw(self, out_file):
        s = "strict graph G { rankdir=LR ratio=fill size=\"9.8, 11\"\n\t"
        for key, attrs in self.vertexes.iteritems():
            s += "\"" + key + " (D: " + str(attrs[0]["dist"]) + ")" +  "\"" + \
                " " + self.__get_right_graphviz_syntax(attrs[0]["color"]) + \
                ";\n\t" + "\"" + key + " (D: " + str(attrs[0]["dist"]) + \
                ")" + "\"" + " -- {"

            """ Continue only if the vertexes doesn't have any
                adjacent one.
            """
            if not attrs[1]["edges"]:
                continue

            for _key, _attrs in attrs[1]["edges"].iteritems():
                # Remove newline characters, if any. Also fix missing
                # backslashs/slashs on parameters and remove duplicate
                # backslashs.
                _key = _key.replace("\n", "").replace(")", "\)"). \
                        replace("(", "\(").replace("]", "\]"). \
                        replace("[", "\[").replace(".", "\."). \
                        replace("?", "\?").replace("*", "\*"). \
                        replace("{", "\{").replace("}", "\}")

                pattern = "^.*" + _key + ".*--.*{"
                if re.match(pattern, s):
                    # ignore duplicates
                    continue

                s += "\"" + _key + " (D: " + str(_attrs[0]["dist"]) + ")" + \
                    "\"" + " " + \
                    self.__get_right_graphviz_syntax(_attrs[0]["color"]) + " "

            s += "};\n\t"

        s += "}\n"

        # .foobar.dot will contain all graphviz syntax to draw our graph
        f = codecs.open('.foobar.dot', 'wa', 'ISO-8859-15', 'replace')
        # write all generated syntaxes to the file
        f.write(s)
        f.close()

        # use dot command for drawing it
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

""" Thread that will run our algorithm and log all its steps. """
class LookupProcess(QtCore.QThread):
    def __init__(self, win, parent=None):
        super(LookupProcess, self).__init__(parent)
        self._win = win

    """ Print @s on the label and save it to be logged afterwards """
    def __print_and_save(self, s):
        self._win.label3.setText(s)
        self._win.log_res += s + "\n"

    """ Breadth-first search algorithm.

        @api        twitter api's object
        @g          graph
        @s          start name
        @e          end name
    """
    def bfs(self, api, g, s, e):
        try:
            users = api.GetFriends(user=self._win.aedit.text())
        except twitter.TwitterError, error:
            self.__print_and_save("<ERROR>: %s" % error)
            return

        # initialize an empty queue for our newly visited vertexes
        queue = []

        # check if exists the start name
        try:
            if not s in [u.name for u in users]:
                raise Exception(s)
        except Exception as inst:
            self.__print_and_save("<ERROR> Could not find user: %s." % \
                                inst.args[0])
            return  # at this point we didn't get the start name :-(

        """ Yeah - we got the start name. So let's add it to the
            graph, set its color to gray and its distance 0 and then
            add it to our queue.

            Note: we're appending a pair of name and id because we
                  need the id to be able to retrieve friends from a
                  given id (the Twitter API claims it).
        """
        g.add_vertex(s, color="gray", dist=0)
        queue.append([s, users[[u.name for u in users].index(s)].screen_name])

        # while the queue isn't empty we can go furth
        while queue:
            first = queue.pop(0)    # remove and get first element of the queue

            self.__print_and_save("<INFO> Looking into %s." % first[0])
            try:
                users = api.GetFriends(user=first[1])
            except twitter.TwitterError, error:
                pattern = "Rate limit exceeded"
                if pattern in error:
                    """ Damnit! We got 150+ twitter requests :-(
                        That's why Twitter allows you to do requests
                        on an 150-request-per-hour boundary.
                    """
                    self.__print_and_save("<ERROR>: %s." % error)
                    return

                if g.vertexes[first[0]][0]["color"] == "black":
                    self.__print_and_save("<WARNING> You're removing a " + \
                                        "black vertex.")

                g.del_vertex(first[0])
                continue
            except urllib2.URLError as inst:
                # We probably got an HTTP error.
                self.__print_and_save("<ERROR> %s." % inst.args[0])
                return

            # iterate over the retrieved users...
            for u in users:
                """ If the u (user) isn't in the graph yet, just add
                    it to the graph and make an edge from
                    first[0] (start vertex) to u.name (end vertex).
                """
                if not u.name in g.vertexes:
                    self.__print_and_save(
                        "<INFO> Adding %s (new vertex) to the Graph" % u.name)
                    g.add_edge(first[0], u.name, color="white", dist=-1)

                """ At this point we've already "u.name" vertex in the
                    Graph. Check if it's a white vertex. If so we set
                    its color to graph and its distance to
                    (first[0]'s distance + 1) and then append it to
                    the queue.
                """
                if g.vertexes[u.name][0]["color"] == "white":
                    val = g.vertexes[first[0]][0]["dist"] + 1
                    g.set_attrs(u.name, color="gray", dist=val)
                    self.__print_and_save(
                        "<INFO> Vertex %s is white - set its color to gray and distance to %d." % (u.name, val))

                    queue.append([u.name, u.screen_name])

                    # check if the vertex is that one we're looking for
                    if u.name == e:
                        # Yeah, we got it motherfucker!!
                        self.__print_and_save(
                            "<INFO> %s has been found! :-) (Distance: %d)" % \
                            (u.name, g.vertexes[u.name][0]["dist"]))
                        # set the found vertex's color to yellow
                        g.set_attrs(u.name, color="yellow")
                        return

            """ If we reached here it means the vertex's adjacents
                have been all visited. So let's set its color to
                black.
            """
            self.__print_and_save(
                "<INFO> Setting color to black for the Vertex %s." % first[0])
            g.set_attrs(first[0], color="black")

    """ This is what the thread will execute once called the start()
        function of the QtCore.QThread object.
    """
    def run(self):
        """ These are specific environment variables which contain
            token numbers to be able to use the Twitter API.
        """
        if not os.environ["CONSUMER_KEY"] or \
            not os.environ["CONSUMER_SECRET"] or \
            not os.environ["ACCESS_TOKEN_KEY"] or \
            not os.environ["ACCESS_TOKEN_SECRET"]:
            self.__print_and_save("<ERROR> There is any missing " + \
                                "environment variable that was not set.")
            return

        """ We got all those environment variables set, so let's get
            the power of the Twitter API! :-)
        """
        api = twitter.Api(
                consumer_key=os.environ["CONSUMER_KEY"],
                consumer_secret=os.environ["CONSUMER_SECRET"],
                access_token_key=os.environ["CONSUMER_SECRET"],
                access_token_secret=os.environ["ACCESS_TOKEN_SECRET"])

        # initialize an empty graph
        g = Graph()
        self.bfs(api, g, self._win.ledit0.text(), self._win.ledit1.text())
        self._win.label2.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        self._win.label2.setText("Please wait. Generating image file from" + \
                            " the generated Graph...")
        # draw an image of the generated graph
        g.draw(image_path)

        """ Emit a signal informing that the thread has finished its
            execution.
        """
        self._win.emit(QtCore.SIGNAL("lookup_process_done"))

class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.initial_layout = QtGui.QGridLayout()

        self.create_initial_layout()
        self.setLayout(self.initial_layout)

        self.setWindowTitle("Project")

    def create_initial_layout(self):
        self.banner = QtGui.QLabel(
                "Copyright (C) 2011 Paulo Alcantara <pcacjr@gmail.com>\n\n" +
                "UNICAP's Graph Classwork")
        self.banner.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        self.adv = QtGui.QLabel("Please, give a starting screen name here:")
        self.adv.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        self.aedit = QtGui.QLineEdit()
        self.label0 = QtGui.QLabel("From: ")
        self.label0.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        self.ledit0 = QtGui.QLineEdit()
        self.label1 = QtGui.QLabel("To: ")
        self.label1.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        self.ledit1 = QtGui.QLineEdit()

        self.go_bt = QtGui.QPushButton("&Go")
        self.go_bt.clicked.connect(self.go_to_final_widget)
        self.quit_bt = QtGui.QPushButton("&Quit")
        self.quit_bt.clicked.connect(QtGui.qApp.quit)

        self.initial_layout.addWidget(self.banner, 1, 0)
        self.initial_layout.addWidget(self.adv, 2, 0)
        self.initial_layout.addWidget(self.aedit, 2, 2)
        self.initial_layout.addWidget(self.label0, 3, 0)
        self.initial_layout.addWidget(self.ledit0, 3, 2)
        self.initial_layout.addWidget(self.label1, 4, 0)
        self.initial_layout.addWidget(self.ledit1, 4, 2)
        self.initial_layout.addWidget(self.go_bt, 5, 0)
        self.initial_layout.addWidget(self.quit_bt, 5, 2)

    def create_loading_animation(self):
        self.loading_label = QtGui.QLabel()
        self.loading_label.setBackgroundRole(QtGui.QPalette.Base)
        self.movie = QtGui.QMovie(loading_image_path)
        self.loading_label.setMovie(self.movie)
        self.movie.start();

    """ Called once the user wanted to abort the lookup proccess. """
    def abort_lookup_process(self):
        mbox = QtGui.QMessageBox()
        mbox.setText("About to abort the lookup process.")
        mbox.setInformativeText("Do you really want to abort the lookup ?")
        mbox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        mbox.setDefaultButton(QtGui.QMessageBox.No)

        ret = mbox.exec_()
        if ret == QtGui.QMessageBox.Yes:
            QtGui.qApp.quit()
        elif ret == QtGui.QMessageBox.No:
            pass

    """ Open an image with the feh command utility. """
    def open_image_with_feh(self):
        os.system("feh " + image_path)

    """ Once the LookupProcess has finished, this function is called
        to write the saved log to the widget which contais the log.
    """
    def write_it_to_log(self):
        self.log.setText(self.log_res)

    """ Save log to a given file. """
    def save_log(self):
        file_format = "txt"
        initial_path = QtCore.QDir.currentPath() + "/log." + file_format
        filename,_ = QtGui.QFileDialog.getSaveFileName(self, "Save Log",
                    initial_path,
                    "%s Files (*.%s);;All Files (*)" % \
                    (str(file_format).upper(), file_format))

        if filename:
            f = codecs.open(filename, 'wa', 'ISO-8859-15', 'replace')
            f.write(self.log.toPlainText())
            f.close()
            self.label2.setText("Cool! The log has been saved in " + filename)

    """ Called once the lookup process has finished. """
    def on_lookup_process_done(self):
        t = QtCore.QTimer(self)
        t.timeout.connect(self.write_it_to_log)
        t.start(1500)

        self.label2.setText("Done! All the steps have been saved " + \
                            "successfully and they're all showed below.")

        self.movie.stop()
        self.movie.setFileName(done_image_path)
        self.movie.start();

        save_log_bt = QtGui.QPushButton("Save Log")
        save_log_bt.clicked.connect(self.save_log)

        open_image = QtGui.QPushButton("Open Image")
        open_image.clicked.connect(self.open_image_with_feh)

        self.final_layout.addWidget(save_log_bt, 5, 2)
        self.final_layout.addWidget(open_image, 3, 2)


    def create_final_layout(self):
        self.w = QtGui.QWidget()

        self.final_layout = QtGui.QGridLayout()

        self.label2 = QtGui.QLabel("Starting lookup...")
        self.label2.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        quit_bt = QtGui.QPushButton("&Quit")
        quit_bt.clicked.connect(self.abort_lookup_process)

        self.log = QtGui.QTextEdit()
        self.log.setReadOnly(True)
        self.log_res = ""

        self.final_layout.addWidget(self.banner, 1, 0)
        self.final_layout.addWidget(quit_bt, 1, 2)
        self.final_layout.addWidget(self.label2, 2, 0)
        self.final_layout.addWidget(self.log, 4, 0)

        self.w.setLayout(self.final_layout)

        self.w.setLayout(self.final_layout)

        self.hide()
        self.w.show()

        self.label2.setText("Please wait. Lookup in progress... " + \
                            "(Looking for %s)" % self.ledit1.text())
        self.label3 = QtGui.QLabel()
        self.label3.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Bold))
        self.final_layout.addWidget(self.label3, 3, 0)

        self.create_loading_animation()
        self.final_layout.addWidget(self.loading_label, 2, 2)

        self.lookup = LookupProcess(self)
        self.lookup.start()

        self.connect(self.lookup, QtCore.SIGNAL("finished()"),
                    self, QtCore.SLOT("on_lookup_process_done()"))

    def go_to_final_widget(self):
        mbox = QtGui.QMessageBox()
        mbox.setText("Damnit! I told you that you _must_ fill in all fields!")
        mbox.setInformativeText("Do you wish to continue ?")
        mbox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        mbox.setDefaultButton(QtGui.QMessageBox.Yes)

        ret = None
        if not self.aedit.text():
            ret = mbox.exec_()
        elif not self.ledit0.text():
            ret = mbox.exec_()
        elif not self.ledit1.text():
            ret = mbox.exec_()

        if ret:
            if ret == QtGui.QMessageBox.Yes:
                pass
            elif ret == QtGui.QMessageBox.No:
                QtGui.qApp.quit()

        self.create_final_layout()
        self.setLayout(self.final_layout)

def main():
    app = QtGui.QApplication(sys.argv)

    win = Window()
    win.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
