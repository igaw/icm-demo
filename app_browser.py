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
import gobject
import dbus

import app_base
import browser

class app_browser(app_base.app_base):
    def __init__(self, stats):
        app_base.app_base.__init__(self, 0, stats)

        self.browser = browser.WebBrowser()

        self.url_idx = 0
        self.urls = [
            "http://www.google.com",
            "http://www.xkcd.org",
            "http://www.lwn.net",
            "http://www.python.org",
            ]

        self.stop_browsing = False

    def browser_new_uri_cb(self):
        if self.stop_browsing:
            return False

        logging.debug("load new url %s" % (self.urls[self.url_idx]))

        if self.url_idx == 0:
            self.browser.content_tabs.new_tab(self.urls[self.url_idx])
        else:
            self.browser.content_tabs.load(self.urls[self.url_idx])
        self.url_idx = self.url_idx + 1

        if self.url_idx >= len(self.urls):
            logging.debug("end of browsing session. release connection")
            self.connection_release()
            self.stop_browsing = True
            return False
        else:
            return True

    def start(self):
        logging.debug("request connection")
        self.connection_request()

    def online(self):
        logging.debug("start browsing")
        self.stop_browsing = False
        self.browser_new_uri_cb()
        gobject.timeout_add_seconds(20, self.browser_new_uri_cb)

    def offline(self):
        self.stop_browsing = True

    def get_widget(self):
        return self.browser.get_widget()
