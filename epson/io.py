#
#  Copyright (C) 2016, Jason S. McMullan <jason.mcmullan@gmail.com>
#  All rights reserved.
#
#  Licensed under the MIT License:
#
#  Permission is hereby granted, free of charge, to any person obtaining
#  a copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import io
import sys
import usb.core


class Io(object):
    """EPSON I/O Transport"""

    def __init__(self):
        pass

    def open(self):
        pass

    def close(self):
        pass

    def send(self, data=None):
        pass

    def recv(self, expected=None):
        return None


class File(Io):
    """EPSON File (Write-Only) Transport"""

    def __init__(self, filename="epson.prn"):
        self.filename = filename
        self.fd = None

    def open(self):
        self.fd = io.open(self.filename, "wb")

    def close(self):
        if self.fd:
            self.fd.close()
            self.fd = None

    def send(self, data):
        if self.fd:
            self.fd.write(data)


def Usb(Io):
    """EPSON USB Transport"""

    def __init__(self, vendor, product, interface=0, out_ep=0x01, in_ep=0x82):
        """
        @param vendor    : Vendor ID
        @param product   : Product ID
        @param interface : USB device interface
        @param out_ep    : Output endpoint
        @param in_ep     : Input endpoint
        """
        self.vendor = vendor
        self.product = product
        self.interface = interface
        self.out_ep = out_ep
        self.in_ep = in_ep

    def open(self):
        dev = usb.core.find(idVendor=self.vendor, idProduct=self.product)
        if dev is None:
            print >> sys.stderr, "epson.io.Usb(): Can't find device!"
            return

        try:
            has_driver = dev.is_kernel_driver_active(0)
            if has_driver:
                try:
                    dev.detach_kernel_driver(0)
                except usb.core.USBError as e:
                    print >> sys.stderr, "Could not detach driver: %s" % str(e)
                    return
        except NotImplementedError:
            pass

        try:
            dev.set_configuration()
            dev.reset()
        except usb.core.USBError as e:
            print >> sys.stderr, "Could not set configuration: %s" % str(e)
            return

        self.device = dev

    def close(self):
        if self.device is not None:
            usb.util.dispose_resources(self.device)
            self.device = None

    def send(self, data):
        self.device.write(self.out_ep, data, self.interface)
