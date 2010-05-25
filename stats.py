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

import gtk

class stats_widget(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self,spacing=1)

        self._id = id

        self.pix_online = gtk.gdk.pixbuf_new_from_file("online.png")
        self.pix_offline = gtk.gdk.pixbuf_new_from_file("offline.png")

        self.icon = gtk.Image()
        self.entry_state = gtk.Entry()
        self.entry_name = gtk.Entry()

        self.icon.set_from_pixbuf(self.pix_offline)
        self.entry_state.set_text("state")
        self.entry_name.set_text("name")

        self.add(self.icon)
        self.add(self.entry_state)
        self.add(self.entry_name)
        self.set_size_request(150,150)

    def set_state(self, state):
        self.entry_state.set_text(state)
        if state in ["ready", "online"]:
            self.icon.set_from_pixbuf(self.pix_online)
        else:
            self.icon.set_from_pixbuf(self.pix_offline)

    def set_name(self, name):
        if name == "":
            self.entry_name.set_text("\"\"")
        else:
            self.entry_name.set_text(name)
