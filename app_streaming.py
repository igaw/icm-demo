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

import streaming
import app_base

class app_streaming(app_base.app_base):
    def __init__(self, stats):
        app_base.app_base.__init__(self, 1, stats)
        self.streaming = streaming.Streaming()

    def start(self):
        logging.debug("start streaming")
        self.connection_request()

    def online(self):
        self.streaming.start("http://www.monom.org/movies/ironman2.ogv")

    def offline(self):
        self.streaming.stop()

    def get_widget(self):
        return self.streaming.get_widget()
