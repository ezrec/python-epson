#!/usr/bin/env python
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

import sys
import struct

protocol = 'escp'

def escp_read(fin = None):
    global protocol

    if protocol == 'remote1':
        code = fin.read(2)
        if len(code) < 2:
            return None

        clen, = struct.unpack("<H", fin.read(2))
        if code == '\033\000' and clen == 0:
            protocol = 'escp'
            return { 'type': protocol, 'code': "\000", 'data': "\000\000" }

        cres, = struct.unpack("<B", fin.read(1))
        data = fin.read(clen-1)
        return { 'type': protocol, 'code': code, 'response': cres, 'data': data }

    ch = fin.read(1)
    if len(ch) < 1:
        return None
    if ch != '\033':
        return { 'type': 'char', 'char': ch }

    if protocol == 'escpr':
        rclass = fin.read(1)
        rlen,   = struct.unpack("<L", fin.read(4))
        rcode  = fin.read(4)
        rdata  = fin.read(rlen)

        escpr = { 'type': 'escpr', 'class': rclass, 'code': rcode }
        if rclass == 'd':
            if rcode == 'dsnd':
                left, top, cmode, dlen = struct.unpack(">HHBH", rdata[0:7])
                rdata = rdata[7:]
                escpr['compress'] = cmode
                escpr['x'] = left
                escpr['y'] = top
                pass
            pass

        if rclass == 'j' and rcode == 'endj':
            protocol = 'escp'

        escpr['data'] = rdata
        return escpr

    code = fin.read(1)
    escp = { 'type': protocol, 'code': code }

    if code == '\001': # Exit packet mode
        data = ""
        nl = 0
        while True:
            ch = fin.read(1)
            data += ch
            if ch == '\n':
                nl = nl + 1
                if nl == 2:
                    escp['data'] = data
                    break
                pass
            pass
        pass
    elif code == '@': # Init printer
        pass
    elif code == 'i': # Raster data
        spec = fin.read(7)
        color, cmode, bpp, bwidth, lines = struct.unpack("<BBBHH", spec)
        data = fin.read(bwidth)
        escp['data'] = spec + data
        escp['bitmap'] = { 'color': color, 'compress': cmode, 'bpp': bpp, 'width': bwidth/bpp*8, 'height': lines }
    elif code == '(': # Extended 
        ecode = fin.read(1)
        elen,  = struct.unpack("<H", fin.read(2))
        data  = fin.read(elen)
        escp['extended'] = ecode
        if ecode == 'R':
            escp['response'] = data[0]
            data = data[1:]
            escp['protocol'] = data
            if data == 'REMOTE1':
                protocol = 'remote1'
            elif data == 'ESCPR' or protocol[1:] == 'ESCPRJ':
                protocol = 'escpr'
        elif ecode == 'v':  # Vertical offset
            escp['offset'], = struct.unpack("<L", data)
        elif ecode == '/':  # Horizontal offset
            escp['offset'], = struct.unpack("<L", data)
        else:
            escp['data'] = data
        pass

    return escp

def main(fin = None, fout = None):
    while True:
        escp = escp_read(fin)
        if escp is None:
            break

        print >>fout, escp
        pass
    return

if __name__ == "__main__":
    main(sys.stdin, sys.stdout)

#  vim: set shiftwidth=4 expandtab: # 
