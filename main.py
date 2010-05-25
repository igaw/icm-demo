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

import gobject
import logging
import gtk
import dbus

import icm.manager
import icm.icm_service

import stats
import app_streaming
import app_browser

class demo(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)

        self.set_decorated(False)
        self.set_keep_above(True)

        self.pixbuf = gtk.gdk.pixbuf_new_from_file("background.png")

        evbox = gtk.EventBox()
        evbox.connect('expose_event', self.expose)

        fixed = gtk.Fixed()

        self.stats_streaming = stats.stats_widget()
        self.stats_browser = stats.stats_widget()
        self.app_streaming = app_streaming.app_streaming(self.stats_streaming)
        self.app_browser = app_browser.app_browser(self.stats_browser)

        fixed.put(self.app_streaming.get_widget(), 20, 50)
        fixed.put(self.app_browser.get_widget(), 290, 50)
        fixed.put(self.stats_streaming, 0, 450)
        fixed.put(self.stats_browser, 160, 450)

        gobject.timeout_add_seconds(1, self.start_streaming)
        gobject.timeout_add_seconds(20, self.start_browser)

        self.set_default_size(800, 600)
        self.connect('destroy', destroy_cb)

        evbox.add(fixed)
        self.add(evbox)

        self.show_all()

    def start_streaming(self):
        self.app_streaming.start()

    def start_browser(self):
        self.app_browser.start()

    def _new_window_requested_cb (self, content_pane, view):
        features = view.get_window_features()
        window = view.get_toplevel()

        scrolled_window = view.get_parent()
        if features.get_property("scrollbar-visible"):
            scrolled_window.props.hscrollbar_policy = gtk.POLICY_NEVER
            scrolled_window.props.vscrollbar_policy = gtk.POLICY_NEVER

        isLocationbarVisible = features.get_property("locationbar-visible")
        isToolbarVisible = features.get_property("toolbar-visible")
        if isLocationbarVisible or isToolbarVisible:
            toolbar = WebToolbar(isLocationbarVisible, isToolbarVisible)
            scrolled_window.get_parent().pack_start(toolbar, False, False, 0)

        window.set_default_size(features.props.width, features.props.height)
        window.move(features.props.x, features.props.y)

        window.show_all()
        return True

    def _title_changed_cb (self, tabbed_pane, frame, title, toolbar):
        self.set_title(_("IVI Connection Management Deno"))
        load_committed_cb(tabbed_pane, frame, toolbar)

    def expose(self, widget, ev):
        widget.window.draw_pixbuf(widget.style.bg_gc[gtk.STATE_NORMAL], self.pixbuf, 0, 0, 0, 0)
        if widget.get_child() != None:
            widget.propagate_expose(widget.get_child(), ev)
        return True



def destroy_cb(window):
    window.destroy()
    gtk.main_quit()

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    gtk.gdk.threads_init()
    demo()
    gtk.main()

if __name__ == "__main__":
    import sys
    import trace

    FORMAT = "%(levelname)s %(filename)-15s %(lineno)3d %(funcName)-20s: %(message)s"
    logging.basicConfig(level = logging.DEBUG, format = FORMAT)

    tracer = trace.Trace(ignoredirs=[sys.prefix, sys.exec_prefix],
                         trace=0,
                         count=1)
    try:
        tracer.run('main()')
    except KeyboardInterrupt:
        r = tracer.results()
        r.write_results(show_missing=True, coverdir="/tmp/icm-demo")
