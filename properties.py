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

import dbus

import gobject
import dbus.mainloop.glib
import logging
import traceback

class _properties_wrapper:
    def __init__(self, callback, user_data):
        self.callback = callback
        self.user_data = user_data

    def reply_handler(self, properties, **keywords):
        self.callback(properties, **keywords)

    def error_handler(self, e):
        logging.error(e)

def get(proxy, dbus_interface, callback, user_data = None):
    clw = _properties_wrapper(callback, user_data)
    proxy.GetProperties(dbus_interface=dbus_interface,
                        reply_handler=clw.reply_handler,
                        error_handler=clw.error_handler)

def create(proxy, dbus_interface, callback, user_data = None):
    proxy.properties_callback = callback
    proxy.properties_user_data = user_data
    proxy.dbus_interface = dbus_interface

    enable(proxy)

def enable(proxy):
    if not proxy.callback:
        return

    proxy.connect_to_signal("PropertyChanged", proxy.properties_callback, proxy.dbus_interface)

def disable(proxy):
    # XXX Is there no way to disconnect from a signal?
    pass

def destroy(proxy):
    disable(proxy)
