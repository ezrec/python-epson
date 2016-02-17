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

import struct
from epson.constant import *

class Image(object):
    """ Base raster class """
    def __init__(self, size = (0, 0)):
        self.size = size[:]

    def bitline(self, y = 0, ci = CI.BLACK, bpp = 1):
        """ Retrieve a bitmap of a line in a single color """
        return ""

    def line(self, y = 0):
        """ Retieve a RGB 24-bit line from the bitmap """
        return ""

class TestImage(Image):
    """ Test Image """

    def bitline(self, y = 0, ci = CI.BLACK, bpp = 1):
        """ Retrieve a bitmap of a line in a single color """

        width = self.size[0]

        # Every 60 lines, change color
        line_color = (y / 60) % 15

        if (line_color & (1 << ci)) == 0:
            return None

        # Return a full raster line
        return chr(0xff) * ((width + 7) / 8) * bpp

    def line(self, y = 0):
        """ Retrieve a RGB 24-bit line from the bitmap """

        if y > self.size[1]:
            return None

        # Every 60 lines, change starting
        color = (y / 60) % 7

        r = ((color >> 0) & 1)
        g = ((color >> 1) & 1)
        b = ((color >> 2) & 1)

        rgb = ""
        for i in range(0, self.size[0]):
            # Fill with gradient
            pos = 256 * i / self.size[0]
            if r:
                r_grad = pos
            else:
                r_grad = 255 - pos
            if g:
                g_grad = pos
            else:
                g_grad = 255 - pos
            if b:
                b_grad = pos
            else:
                b_grad = 255 - pos
            rgb += struct.pack("BBB", r_grad, g_grad, b_grad)
            pass
        
        return rgb


#  vim: set shiftwidth=4 expandtab: # 
