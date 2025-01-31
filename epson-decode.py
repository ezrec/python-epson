#!/usr/bin/env python3
#
# Decode an ESC/P file into a human-readable format
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

import sys
import struct

protocol = "escp"


def rle_read(fin=None, blen=0, cmode=False):
    if not cmode:
        return fin.read(blen)

    data = b""
    while blen > 0:
        c = ord(fin.read(1))
        if c < 0x80:
            data += fin.read(c + 1)
            blen -= c + 1
        else:
            element = fin.read(1)
            data += element * (257 - c)
            blen -= 257 - c

    return data


def escp_read(fin=None):
    global protocol

    if protocol == "remote1":
        code = fin.read(2)
        if len(code) < 2:
            return None

        (clen,) = struct.unpack("<H", fin.read(2))
        if code == b"\033\000" and clen == 0:
            protocol = "escp"
            return {"type": protocol, "code": b"\000", "data": b"\000\000"}

        (cres,) = struct.unpack("<B", fin.read(1))
        data = fin.read(clen - 1)
        escp = {"type": protocol, "code": code, "response": cres}
        if code == "TI":
            date = struct.unpack(">HBBBBB", data)
            escp["date"] = "%d-%d-%d,%d:%02d:%02d" % date
        else:
            escp["data"] = data

        return escp

    ch = fin.read(1)
    if len(ch) < 1:
        return None

    if ch != b"\033":
        return {"type": "char", "char": ch}

    if protocol == "escpr":
        rclass = fin.read(1)
        (rlen,) = struct.unpack("<L", fin.read(4))
        rcode = fin.read(4)
        rdata = fin.read(rlen)

        escpr = {"type": "escpr", "class": rclass, "code": rcode}
        if rclass == b"d":
            if rcode == b"dsnd":
                left, top, cmode, dlen = struct.unpack(">HHBH", rdata[0:7])
                rdata = rdata[7:]
                escpr["compress"] = cmode
                escpr["x"] = left
                escpr["y"] = top
        elif rclass == b"j":
            if rcode == b"endj":
                protocol = "escp"
            elif rcode == b"setj":
                width, height, top, left, rwidth, rheight, ir, pd = struct.unpack(
                    ">LLHHLLBB", rdata
                )
                escpr["paper"] = (width, height)
                escpr["margin"] = (
                    left,
                    top,
                    (width - left - rwidth),
                    (height - top - rheight),
                )
                dpi = 360
                if ir == 0:
                    dpi = 360
                elif ir == 1:
                    dpi = 720
                elif ir == 2:
                    dpi = 300
                elif ir == 3:
                    dpi = 600
                escpr["dpi"] = dpi
                escpr["pd"] = pd
                rdata = None
        elif rclass == b"q":
            if rcode == b"setq":
                mtid, mqid, cm, brightness, contrast, saturation, cp, plen = (
                    struct.unpack(">BBBbbbBH", rdata[0:9])
                )
                palette = rdata[9:]
                escpr["mtid"] = mtid
                escpr["mqid"] = mqid
                escpr["cm"] = cm
                escpr["brightness"] = brightness
                escpr["contrast"] = contrast
                escpr["saturation"] = saturation
                escpr["cp"] = cp
                if len(palette) == 0:
                    palette = None
                escpr["palette"] = palette

        if rdata is not None and len(rdata) > 0:
            escpr["data"] = rdata

        return escpr

    code = fin.read(1)
    escp = {"type": protocol, "code": code}

    if code == b"\001":  # Exit packet mode
        data = b""
        nl = 0
        while True:
            ch = fin.read(1)
            data += ch
            if ch == b"\n":
                nl = nl + 1
                if nl == 2:
                    escp["data"] = data
                    break
    elif code == b"@":  # Init printer
        pass
    elif code == b"i":  # Raster data
        spec = fin.read(7)
        color, cmode, bpp, bwidth, lines = struct.unpack("<BBBHH", spec)
        data = rle_read(fin, bwidth, cmode)
        escp["color"] = color
        escp["compress"] = cmode
        escp["bpp"] = bpp
        escp["width"] = int(bwidth / bpp * 8)
        escp["height"] = lines
        escp["raster"] = data
    elif code == b"(":  # Extended
        ecode = fin.read(1)
        (elen,) = struct.unpack("<H", fin.read(2))
        data = fin.read(elen)
        escp["extended"] = ecode
        if ecode == b"R":
            escp["response"] = data[0]
            data = data[1:]
            escp["protocol"] = data
            if data == b"REMOTE1":
                protocol = "remote1"
            elif data == b"ESCPR" or data == b"ESCPRJ":
                protocol = "escpr"

        elif ecode == b"v":
            # Set absolute vertical print position.
            if elen == 2:
                # Version 1.00.
                (escp["offset"],) = struct.unpack("<H", data)
            elif elen == 4:
                # Version 2.00. Extended.
                (escp["offset"],) = struct.unpack("<L", data)
            else:
                raise ValueError(f"Incorrect parameters size '{elen}'.")

        elif ecode == b"/":  # Horizontal offset
            (escp["offset"],) = struct.unpack("<L", data)
        else:
            escp["data"] = data

    return escp


def main(fin=None):
    while True:
        escp = escp_read(fin)
        if escp is None:
            break

        print(escp)


if __name__ == "__main__":
    try:
        # Python3
        fin = sys.stdin.buffer
    except:
        fin = sys.stdin

    main(fin)
