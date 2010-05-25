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

import logging
import properties
import dbus
import gobject
import multiprocessing
import collections

class interface_handler():
    def __init__(self, sender, mutex, name, bus, uid, dbus_name, dbus_interface, attr, interface_cb):
        self._sender = sender
        self._mutex = mutex
        self._name = name
        self._bus = bus
        self._uid = uid
        self._dbus_name = dbus_name
        self._dbus_interface = dbus_interface
        self._attr = attr
        self._interface_cb = interface_cb
        self._proxy = None

    def update_properties(self):
        self._proxy = self._bus.get_object(self._dbus_name, self._uid)
        properties.create(self._proxy, self._dbus_interface, self.property_changed)
        
        props = self._proxy.GetProperties(dbus_interface = self._dbus_interface)
        self.properties_init(props)

    def properties_init(self, properties):
        self._mutex.acquire()

        for key, value in properties.items():
            #logging.debug("%s: init property '%s' '%s' - '%s'" % (self._uid, self._dbus_interface, str(key), str(value)))
            self._add_attr(self._attr, key, value)

        for key, value in self._attr.items():
            self._sender.notify(key, value)

        self._mutex.release()

        if "Interfaces" in self._attr:
            self._interface_cb(self._attr["Interfaces"])

    def property_changed(self, key, value):
        self._mutex.acquire()

        #logging.debug("%s: property '%s' changed - '%s'" % (self._uid, str(key), str(value)))
        self._add_attr(self._attr, key, value)
        self._sender.notify(key, value)

        self._mutex.release()

        if "Interfaces" in self._attr:
            self._interface_cb(self._attr["Interfaces"])

    def add_interface(self, name, dbus_interface):
        self._interfaces.append(name)

    def _add_attr(self, d, key, value):
        #logging.debug("key %s, value %s" % (type(key).__name__, type(value).__name__))
        if type(value).__name__ == "Dictionary":
            d[key] = collections.defaultdict(lambda: "<missing>")
            for (k,v) in value.items():
                self._add_attr(d[key], k, v)
        else:
            d[key] = value
        
class dbus_object(gobject.GObject):
    __gsignals__ = {
        "property-changed": (gobject.SIGNAL_RUN_FIRST,
                             gobject.TYPE_NONE,
                             (gobject.TYPE_STRING, object,)),
        }

    def __init__(self, bus, dbus_name, uid, name):
        gobject.GObject.__init__(self)
        logging.debug("new %s object for '%s'" % (name, uid))
        self._bus = bus
        self._dbus_name = dbus_name
        self._uid = uid
        self._name = name
        self._interfaces = {}
        self._mutex = multiprocessing.Lock()

    def __repr__(self):
        return "<%s %s>" % (self._name, self._uid)

    def notify(self, key, value):
        tkey = key.lower()
        tkey = tkey.replace(".", "")
        tkey = "%s_%s" % (self._name, tkey)

        #logging.debug("emit property-changed '%s' = '%s'" % (tkey, value))
        self.emit("property-changed", tkey, value)

    def handle_interfaces(self, interfaces):
        # remove all interfaces which disappeared
        for ifs in self._interfaces.keys():
            if ifs not in interfaces:
                self.remove_interface(ifs)

        # add all interfaces which appeared
        for ifs in interfaces:
            if ifs not in self._interfaces.keys():
                self.add_interface(ifs)

    def add_interface(self, name):
        pass

    def remove_interface(self, name):
        pass

    def register_interface(self, dbus_interface, attr):
        self._interfaces[dbus_interface] = interface_handler(self,
                                                             self._mutex,
                                                             self._name,
                                                             self._bus,
                                                             self._uid,
                                                             self._dbus_name,
                                                             dbus_interface,
                                                             attr,
                                                             self.handle_interfaces)

    def unregister_interface(self, dbus_interface):
        del self._interfaces[dbus_interface]

    def update_properties(self, dbus_interface = None):
        if dbus_interface == None:
            for key, value in self._interfaces.items():
                logging.debug("update properties for interface '%s'" % (key))
                value.update_properties()
        else:
            self._interfaces[dbus_interface].update_properties()

    def get_interface(self, dbus_interface):
        return dbus.Interface(self._interfaces[dbus_interface]._proxy, dbus_interface)
