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
import traceback
import logging
import dbus

import icm.icm_service
import icm.manager

class app_base(gobject.GObject):
    def __init__(self, id, stats):
        gobject.GObject.__init__(self)
        self._id = id
        self._stats = stats
        self._bus = dbus.SystemBus()
        self.hid = None

        # icm dbus objects
        self._icm_manager = None
        self._icm_service_path = None
        self._icm_service = None

        try:
            self._bus.watch_name_owner('de.bmwcarit.icm', self.icm_name_owner_changed)
        except dbus.DBusException:
            traceback.print_exc()
            exit(1)

    def icm_name_owner_changed(self, proxy):
        try:
            logging.debug(str(proxy))

            if proxy:
                self._icm_manager = icm.manager.Manager(self._bus, "/")
            else:
                self._icm_manager = None
                self._icm_service = None
                self._icm_service_path = None

        except dbus.DBusException:
            traceback.print_exc()
            exit(1)

    def connection_request(self):
        if self._icm_manager != None and self._icm_service_path == None:
            self._icm_service_path = self._icm_manager.CreateIcmService(self._id)

        if self._icm_service_path != None and self._icm_service == None:
            logging.debug("add icm service object proxy %s" % (self._icm_service_path))
            self._icm_service = icm.icm_service.IcmService(self._bus, self._icm_service_path)

            self.hid = self._icm_service.connect("property-changed", self.property_changed)

        self._icm_service.ConnectionRequest()

    def connection_release(self):
        if self._icm_service:
            logging.debug("release connection")
            self._icm_service.ConnectionRelease()

        
    def cleanup(self):
            logging.debug("remove icm service object proxy %s" % (self._icm_service_path))
            self._icm_service.Disconnect(self.hid)
            
            self._icm_manager.DestroyIcmService(self._icm_service_path)

    def start(self):
        pass

    def property_changed(self, service, key, value):
        if key == "icm_icm_service_state":
            self._handle_state(value)
        elif key == "icm_icm_service_name":
            self._handle_name(value)

    def _handle_state(self, state):
        logging.debug("state changed for %s to '%s'" % (self._icm_service_path, state))
        self._stats.set_state(state)

        if state in ["ready", "online"]:
            self.online()
        else:
            self.offline()

    def online(self):
        pass

    def offline(self):
        pass


    def _handle_name(self, name):
        self._stats.set_name(name)
