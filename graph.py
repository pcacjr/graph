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

image_path = "/home/pcacjr/src/other-graph/images/file.png"
loading_image_path = "/home/pcacjr/src/other-graph/images/loading.gif"
done_image_path = "/home/pcacjr/src/other-graph/images/done.gif"

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

    def set_attrs(self, v, **kwargs):
        if v not in self.vertexes:
            return

        for key, attrs in self.vertexes.iteritems():
            if key == v:
                for k in kwargs:
                    attrs[0][k] = kwargs[k]

            for _key, _attrs in attrs[1]["edges"].iteritems():
                if _key == v:
                    for k in kwargs:
                        _attrs[0][k] = kwargs[k]

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
            s += "\"" + key + " (D: " + str(attrs[0]["dist"]) + ")" +  "\"" + \
                " " + self.__get_right_graphviz_syntax(attrs[0]["color"]) + \
                ";\n\t" + "\"" + key + " (D: " + str(attrs[0]["dist"]) + \
                ")" + "\"" + " -- {"

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

        f = codecs.open('.foobar.dot', 'wa', 'ISO-8859-15', 'replace')
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

# Thread that will run our algorithm :-)
class LookupProcess(QtCore.QThread):
    def __init__(self, win, parent=None):
        super(LookupProcess, self).__init__(parent)
        self._win = win

    def __print_and_save(self, s):
        self._win.label3.setText(s)
        self._win.log_res += s + "\n"

    def bfs(self, api, g, s, e):
        try:
            users = api.GetFriends(user=self._win.aedit.text())
        except twitter.TwitterError, error:
            self.__print_and_save("<ERROR>: %s" % error)
            return

        queue = []

        try:
            if not s in [u.name for u in users]:
                raise Exception(s)
        except Exception as inst:
            self.__print_and_save("<ERROR> Could not find user: %s." % \
                                inst.args[0])
            return

        g.add_vertex(s, color="gray", dist=0)
        queue.append([s, users[[u.name for u in users].index(s)].screen_name])

        while queue:
            first = queue.pop(0)    # remove and get first element of the queue

            self.__print_and_save("<INFO> Looking into %s." % first[0])
            try:
                users = api.GetFriends(user=first[1])
            except twitter.TwitterError, error:
                if g.vertexes[first[0]][0]["color"] == "black":
                    self.__print_and_save("<WARNING> You're removing a " + \
                                        "black vertex.")

                g.del_vertex(first[0])
                continue

            for u in users:
                if not u.name in g.vertexes:
                    self.__print_and_save(
                        "<INFO> Adding %s (new vertex) to the Graph" % u.name)
                    g.add_edge(first[0], u.name, color="white", dist=-1)

                if g.vertexes[u.name][0]["color"] == "white":
                    val = g.vertexes[first[0]][0]["dist"] + 1
                    g.set_attrs(u.name, color="gray", dist=val)
                    self.__print_and_save(
                        "<INFO> Vertex %s is white - set its color to gray and distance to %d." % (u.name, val))

                    queue.append([u.name, u.screen_name])

                    if u.name == e:
                        self.__print_and_save(
                            "<INFO> %s has been found! :-) (Distance: %d)" % \
                            (u.name, g.vertexes[u.name][0]["dist"]))
                        # set the found vertex's color to yellow
                        g.set_attrs(u.name, color="yellow")
                        return

            self.__print_and_save(
                "<INFO> Setting color to black for the Vertex %s." % first[0])
            g.set_attrs(first[0], color="black")

    def run(self):
        if not os.environ["CONSUMER_KEY"] or \
            not os.environ["CONSUMER_SECRET"] or \
            not os.environ["ACCESS_TOKEN_KEY"] or \
            not os.environ["ACCESS_TOKEN_SECRET"]:
            self.__print_and_save("<ERROR> There is any missing " + \
                                "environment variable that was not set.")
            return

        api = twitter.Api(
                consumer_key=os.environ["CONSUMER_KEY"],
                consumer_secret=os.environ["CONSUMER_SECRET"],
                access_token_key=os.environ["CONSUMER_SECRET"],
                access_token_secret=os.environ["ACCESS_TOKEN_SECRET"])

        g = Graph()
        self.bfs(api, g, self._win.ledit0.text(), self._win.ledit1.text())
        self._win.label2.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        self._win.label2.setText("Please wait. Generating image file from" + \
                            " the generated Graph...")
        g.draw(image_path)

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

    def open_image_with_feh(self):
        os.system("feh " + image_path)

    def write_it_to_log(self):
        self.log.setText(self.log_res)

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
