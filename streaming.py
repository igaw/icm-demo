#  IVI Connection Manager
#
#  Copyright (C) 2010  BMW Car IT GmbH. All rights reserved.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License version 2 as
#  published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys, os
import pygtk, gtk, gobject
import pygst
pygst.require("0.10")
import gst

class Streaming:
    def __init__(self):

        self.vbox = gtk.VBox()
        hbox = gtk.HBox()
        self.vbox.pack_start(hbox, False)
        self.entry = gtk.Entry()
        hbox.add(self.entry)
        self.button = gtk.Button("Start")
        hbox.pack_start(self.button, False)
        self.button.connect("clicked", self.start_stop)
        self.movie_window = gtk.DrawingArea()
        self.vbox.add(self.movie_window)

        self.vbox.set_size_request(260,200)

        self.player = gst.element_factory_make("playbin2", "player")
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

    def get_widget(self):
        return self.vbox

    def start_stop(self, w):
        if self.button.get_label() == "Start":
            uri = self.entry.get_text()
            self.button.set_label("Stop")
            self.player.set_property("uri", uri)
            self.player.set_state(gst.STATE_PLAYING)
        else:
            self.player.set_state(gst.STATE_NULL)
            self.button.set_label("Start")

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.button.set_label("Start")
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.button.set_label("Start")

    def on_sync_message(self, bus, message):
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            gtk.gdk.threads_enter()
            imagesink.set_xwindow_id(self.movie_window.window.xid)
            gtk.gdk.threads_leave()

    def start(self, uri):
        self.button.set_label("Stop")
        self.entry.set_text(uri)
        self.player.set_property("uri", uri)
        self.player.set_state(gst.STATE_PLAYING)

    def stop(self):
        self.button.set_label("Start")
        self.player.set_state(gst.STATE_NULL)
