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

import collections
import dbus_object

class IcmService(dbus_object.dbus_object):
    def __init__(self, bus, uid):
        dbus_object.dbus_object.__init__(self, bus, "de.bmwcarit.icm", uid, "icm_icm_service")

        self._attr = collections.defaultdict(lambda: "<missing>")
        self.register_interface("de.bmwcarit.icm.IcmService", self._attr)

        self.update_properties()

    @property
    def uid(self):
        return self._uid

    @property
    def attributes(self):
        return self._attr

    #############################################################################

    def ConnectionRequest(self):
        return self.get_interface("de.bmwcarit.icm.IcmService").ConnectionRequest()

    def ConnectionRelease(self):
        self.get_interface("de.bmwcarit.icm.IcmService").ConnectionRelease()

    @property
    def State(self):
        return self._attr["State"]

    @property
    def RX_Bytes(self):
        return self._attr["RX.Bytes"]

    @property
    def TX_Bytes(self):
        return self._attr["TX.Bytes"]

    @property
    def Name(self):
        return self._attr["Name"]

