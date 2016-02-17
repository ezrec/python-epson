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
import time
import struct
from epson.constant import *

class Interface(object):
    """ Base class for accessing EPSON ESC/P Raster printers """

    # Exit packet mode
    ExitPacketMode = b"\000\000\000\033\001@EJL 1284.4\n@EJL     \n"
    # Initilaize printer
    InitPrinter = b"\033@"

    # REMOTE1 protocol commands
    # Enter remote mode
    EnterRemoteMode = b"\033(R\010\000\000REMOTE1"
    ExitRemoteMode = b"\033\000\000\000"

    # Initialize time of day.
    # data = YYYY(be16), MM(8), DD(8), hh(8), mm(8), ss(8) 
    RemoteTimeInit = b"TI"

    # Mark start of job
    # data = 0, 0, 0
    RemoteJobStart = b"JS"

    # Name the job
    # data = 0, 0, 0, 0, 0, "Name-of-job"
    RemoteJobHeader = b"JH"

    # Hardware Device (source platform)
    # data = 3, 4 (4 == Linux)
    RemoteHardwareDevice = b"HD"

    # PaperPath
    # data = dst, src
    RemotePaperPath = b"PP"

    # DuplexPath
    # data = 2
    RemoteDuplexPath = b"DP"
    # No data
    RemoteLeaveDuplex = b"LD"

    # Job End
    RemoteJobEnd = b"JE"

    def __init__(self, io = None):
        """ Initialize class """
        self.io = io
        self.last_job = 0
        pass

    def _send(self, msg):
        self.io.send(msg)
        pass

    def _recv(self, expected = 0):
        return self.io.recv(expected = expected)

    """ Low-level command wrapper functions """
    def _exit_packet_mode(self):
        self._send(self.ExitPacketMode)
        pass

    def _init_printer(self):
        self._send(self.InitPrinter)
        pass

    def _form_feed(self):
        self._send(byte(0xc))

    def _remote1_enter(self):
        self._send(self.EnterRemoteMode)
        pass

    def _remote1_cmd(self, cmd, data = b"", response = 0):
        self._send(cmd + struct.pack("<H", len(data) + 1) + byte(response) + data)
        pass

    def _remote1_exit(self):
        self._send(self.ExitRemoteMode)
        pass

    """ REMOTE1 Commands """
    def _time_init(self):
        now = time.localtime()
        data = struct.pack(">HBBBBB", now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        self._remote1_cmd(self.RemoteTimeInit, data)
        pass

    def _job_start(self, name = None):
        if name is None:
            data = b"\000\000\000"
        else:
            data = name.encode() + b"\000"
        self._remote1_cmd(self.RemoteJobStart, data)
        pass

    def _job_end(self):
        self._remote1_cmd(self.RemoteJobEnd)
        pass

    def _job_header(self, job_type = 0, job_name = "ESCPPRLib", job_id = None):
        if job_id == None:
            job_id = self.last_job
        data = byte(job_type) + struct.pack(">L", job_id) + job_name.encode()
        self._remote1_cmd(self.RemoteJobHeader, data)
        self.last_job = job_id + 1
        pass

    def _hardware_device(self, platform = 4):
        data = b"\003" + byte(platform)
        self._remote1_cmd(self.RemoteHardwareDevice, data)
        pass

    def _paper_path(self, mpid = MPID.AUTO):
        dst = 1
        src = 0
        if mpid == MPID.REAR:
            dst = 1
            src = 0
        elif mpid == MPID.FRONT1:
            dst = 1
            src = 1
        elif mpid == MPID.FRONT2:
            dst = 1
            src = 2
        elif mpid == MPID.FRONT3:
            dst = 1
            src = 3
        elif mpid == MPID.FRONT4:
            dst = 1
            src = 4
        elif mpid == MPID.CDTRAY:
            dst = 2
            src = 1
        elif mpid == MPID.ROLL:
            dst = 3
            src = 0
        elif mpid == MPID.MANUAL:
            dst = 2
            src = 0
        else: # mpid == MPID.AUTO, or any other
            dst = 1
            src = 0xff # Autoselect

        data = byte(dst) + byte(src)
        self._remote1_cmd(self.RemotePaperPath, data)
        pass

    def _duplex(self, duplex = False):
        if duplex:
            data = "\002"
            self._remote1_cmd(self.RemoteDuplexPath, data)
        else:
            self._remote1_cmd(self.RemoteLeaveDuplex)
        pass

    """ Printing method control """
    def _direction(self, pd = PD.BIDIREC):
        self._send(b"\033U" + byte(pd))
        pass

    def _color_mode(self, cm = CM.COLOR):
        self._send(b"\033(K" + byte(1) + byte(0) + byte(0) + byte(cm))
        pass

    def _image_resolution(self, dpi = 360):
        if (dpi % 360) == 0:
            r = 1440
        else:
            r = 1200
        v = r / dpi
        h = r / dpi
        data = struct.pack("<HHBB", 4, r, v, h)
        self._send(b"\033(D" + data)
        pass

    def _set_unit(self, p_dpi = 360, h_dpi = 360, v_dpi = 360):
        base = 1440
        p = base / p_dpi
        h = base / h_dpi
        v = base / v_dpi
        data = struct.pack("<HBBBH", 5, p, v, h, base)
        self._send(b"\033(U" + data)

    def _page_format(self, msid = MSID.LETTER, margin = (0, 0, 0, 0), dpi = 360):
        mm2in = 1.0/25.4
        self._image_resolution(dpi = dpi)
        self._set_unit(p_dpi = dpi, h_dpi = dpi, v_dpi = dpi)
        y_top = int(margin[1] * mm2in * dpi)
        y_bottom = int((msid[1] - margin[3]) * mm2in * dpi)
        x_left = int(margin[0] * mm2in * dpi)
        x_right = int(margin[2] * mm2in * dpi)
        data = struct.pack("<HLL", 8, y_top, y_bottom)
        self._send(b"\033(c" + data)

        return (x_right - x_left, y_bottom - y_top)

    def _vertical_position(self, y = 0, dpi = 360):
        mm2in = 1.0/25.4
        data = struct.pack("<HL", 4, int(y * mm2in * dpi))
        self._send(b"\033(v" + data)
        pass

    def _horizontal_position(self, x = 0, dpi = 360):
        mm2in = 1.0/25.4
        data = struct.pack("<HL", 4, int(x * mm2in * dpi))
        self._send(b"\033(/" + data)
        pass

    def _send_line(self, color = CI.BLACK, line = None, bpp = 1):
        if line is None or len(line) == 0:
            return

        compressed = False
        if compressed:
            cmode = 1
        else:
            cmode = 0

        data = struct.pack("<BBBHH", color, cmode, bpp,
                           len(line), 1)
        data += line
        self._send(b"\033i" + data)
        pass
                            
class Job(Interface):
    """ EPSON ESC/P 'ESC ( D' Job Wrapper """

    def __init__(self, io = None, name = "ESCPLib"):
        super(Job, self).__init__(io = io)

        # Job name
        self.name = name

        # Output selection
        self.dpi = 300
        self.pd = PD.BIDIREC

        # Paper path
        self.mpid = MPID.AUTO
        self.duplex = False

        self.cm = CM.COLOR

        # JPEG auto photo fix
        self.act = ACT.NOTHING
        self.sharpness = 0
        self.rde = RDE.NOTHING

        # Quality settings
        self.mqid = MQID.DRAFT
        self.cm = CM.COLOR
        self.brightness = 0
        self.contrast = 0
        self.saturation = 0
        self.cp = CP.FULLCOLOR
        self.palette = None

        # Size parameters
        self.mtid = MTID.PLAIN
        self.msid = MSID.LETTER
        self.mlid = MLID.BORDERS
        self.margin = (3, 3, 3, 3) # 3mm borders

        # CD Label size
        self.cddim_id = None
        self.cddim_od = None

    def _start(self, copies = 1):
        if self.mtid == MTID.CDDVD or self.mtid == MTID.CDDVDHIGH or self.mtid == MTID.CDDVDGLOSSY:
           self.mpid = MPID.CDTRAY
           self.mlid = MLID.CDLABEL

        self._exit_packet_mode()
        self._init_printer()

        # REMOTE commands
        self._remote1_enter()
        self._time_init()
        self._job_start()
        self._job_header(job_name = self.name)
        self._hardware_device()

        self._paper_path(self.mpid)
        self._duplex(self.duplex)

        self._remote1_exit()

        # ESC/P setup commands
        self._direction(pd = self.pd)
        self._color_mode(cm = self.cm)
        size = self._page_format(msid = self.msid, margin = self.margin, dpi = self.dpi)

        return size

    def _end(self):
        self._init_printer()

        self._remote1_enter()
        if self.duplex:
            self._duplex(False)

        self._job_end()
        self._remote1_exit()

    def print_pages(self, rasters = None, bpp = 1):

        size = self._start()

        for raster in rasters:
            delta_y = self.margin[1]

            for y in range(0, min(size[1], raster.size[1])):
                self._vertical_position(y = delta_y, dpi = self.dpi)
                self._horizontal_position(x = self.margin[0], dpi = self.dpi)

                for color in range(0,4):
                    line = raster.bitline(y = y, ci = color, bpp = bpp)
                    self._send_line(line = line, bpp = bpp)

                delta_y = 25.4 / self.dpi
            pass

            self._form_feed()
        pass

        self._end()
        pass


#  vim: set shiftwidth=4 expandtab: # 
