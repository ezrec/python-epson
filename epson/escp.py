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

import time
import struct
from typing import Optional
from epson.constant import *
from epson.raster import Image


class Interface(object):
    """Base class for accessing EPSON ESC/P Raster printers"""

    # Exit packet mode
    ExitPacketMode = b"\x00\x00\x00\x1b\x01@EJL 1284.4\n@EJL     \n"
    # Initilaize printer
    InitPrinter = b"\x1b@"

    # REMOTE1 protocol commands
    # Enter remote mode
    EnterRemoteMode = b"\x1b(R\x08\x00\x00REMOTE1"
    ExitRemoteMode = b"\x1b\x00\x00\x00"

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

    def __init__(self, io=None):
        """Initialize class"""
        self.io = io
        self.last_job = 0

    def _send(self, msg):
        self.io.send(msg)

    def _recv(self, expected=0):
        return self.io.recv(expected=expected)

    """ Low-level command wrapper functions """

    def _exit_packet_mode(self):
        self._send(self.ExitPacketMode)

    def _init_printer(self):
        self._send(self.InitPrinter)

    def _form_feed(self):
        self._send(byte(0xC))

    def _remote1_enter(self):
        self._send(self.EnterRemoteMode)

    def _remote1_cmd(self, cmd, data=b"", response=0):
        self._send(cmd + struct.pack("<H", len(data) + 1) + byte(response) + data)

    def _remote1_exit(self):
        self._send(self.ExitRemoteMode)

    """ REMOTE1 Commands """

    def _time_init(self):
        now = time.localtime()
        data = struct.pack(
            ">HBBBBB",
            now.tm_year,
            now.tm_mon,
            now.tm_mday,
            now.tm_hour,
            now.tm_min,
            now.tm_sec,
        )
        self._remote1_cmd(self.RemoteTimeInit, data)

    def _job_start(self, name=None):
        if name is None:
            data = b"\x00\x00\x00"
        else:
            data = name.encode() + b"\x00"
        self._remote1_cmd(self.RemoteJobStart, data)

    def _job_end(self):
        self._remote1_cmd(self.RemoteJobEnd)

    def _job_header(self, job_type=0, job_name="ESCPPRLib", job_id=None):
        if job_id == None:
            job_id = self.last_job
        data = byte(job_type) + struct.pack(">L", job_id) + job_name.encode()
        self._remote1_cmd(self.RemoteJobHeader, data)
        self.last_job = job_id + 1

    def _hardware_device(self, platform=4):
        data = b"\x03" + byte(platform)
        self._remote1_cmd(self.RemoteHardwareDevice, data)

    def _paper_path(self, mpid=MPID.AUTO):
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
        else:  # mpid == MPID.AUTO, or any other
            dst = 1
            src = 0xFF  # Autoselect

        data = byte(dst) + byte(src)
        self._remote1_cmd(self.RemotePaperPath, data)

    def _duplex(self, duplex=False):
        if duplex:
            data = "\x02"
            self._remote1_cmd(self.RemoteDuplexPath, data)
        else:
            self._remote1_cmd(self.RemoteLeaveDuplex)

    """ Printing method control """

    def _direction(self, pd=PD.BIDIREC):
        self._send(b"\x1bU" + byte(pd))

    def _send_ext(self, code, data=None):
        self._send(b"\x1b(" + code + struct.pack("<H", len(data)) + data)

    def _graphics_mode(self):
        self._send_ext(b"G", struct.pack("<B", 1))

    def _color_mode(self, cm=CM.COLOR):
        self._send_ext(b"K", struct.pack("<BB", 0, cm))

    def _image_resolution(self, h_dpi=360, v_dpi=120):
        base = 1440
        v = base // h_dpi
        h = base // v_dpi
        data = struct.pack("<HBB", base, v, h)
        self._send_ext(b"D", data)

    def _set_unit(self, p_dpi=360, h_dpi=360, v_dpi=360):
        base = max([p_dpi, h_dpi, v_dpi])
        if base == min([p_dpi, h_dpi, v_dpi]):
            # Use the non-extended version (since all DPIs are the same)
            data = struct.pack("<B", 3600 // p_dpi)
            self._send_ext(b"U", data)
        else:
            # Use the extended version (for differing DPIs)
            p = base // p_dpi
            h = base // h_dpi
            v = base // v_dpi
            data = struct.pack("<BBBH", p, v, h, base)
            self._send_ext(b"U", data)

    def _page_format(self, msid=MSID.LETTER, margin=(0, 0, 0, 0), dpi=360):
        mm2in = 1.0 / 25.4
        y_top = int(margin[1] * mm2in * dpi)
        y_bottom = int((msid[1] - margin[3]) * mm2in * dpi)
        x_left = int(margin[0] * mm2in * dpi)
        x_right = int(margin[2] * mm2in * dpi)
        data = struct.pack("<LL", y_top, y_bottom)
        self._send_ext(b"c", data)

        return (x_right - x_left, y_bottom - y_top)

    def _dot_size(self, dpi=360):
        # FIXME: Determine the correct dot size
        # dot_size = ??
        # self._send_ext(b"e", struct.pack("<BB", 0, dot_size))
        pass

    def _vertical_position(self, y=0):
        data = struct.pack("<L", y)
        self._send_ext(b"V", data)

    def _vertical_increment(self, y=0):
        data = struct.pack("<L", y)
        self._send_ext(b"v", data)

    def _horizontal_position(self, x=0):
        data = struct.pack("<L", x)
        self._send_ext(b"$", data)

    def _horizontal_increment(self, x=0):
        data = struct.pack("<L", x)
        self._send_ext(b"/", data)

    def _paper_dimension(self, msid=(0, 0), dpi=360):
        mm2in = 1.0 / 25.4
        width = int(round(msid[0] * mm2in * dpi))
        height = int(round(msid[1] * mm2in * dpi))
        data = struct.pack("<LL", width, height)
        self._send_ext(b"S", data)

    def _print_method(self, method=0x12):
        self._send_ext(b"m", struct.pack("<B", method))

    def _send_line(
        self,
        color=CI.BLACK,
        line: Optional[bytes] = None,
        bpp=1,
        compressed=True,
    ):
        if line is None or len(line) == 0:
            return

        if compressed:
            cmode = 1
        else:
            cmode = 0

        data = struct.pack("<BBBHH", color, cmode, bpp, len(line), 1)
        if compressed:
            data += run_length_encode(line, bytes_per_pixel=1)
        else:
            data += line

        self._send(b"\x1bi" + data)


class Job(Interface):
    """EPSON ESC/P 'ESC ( D' Job Wrapper"""

    def __init__(self, io=None, name="ESCPLib"):
        super(Job, self).__init__(io=io)

        # Job name
        self.name = name

        # Output selection
        self.dpi = 360
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
        self.margin = (3, 3, 3, 3)  # 3mm borders

        # CD Label size
        self.cddim_id = None
        self.cddim_od = None

    def _start(self, copies=1):
        if (
            self.mtid == MTID.CDDVD
            or self.mtid == MTID.CDDVDHIGH
            or self.mtid == MTID.CDDVDGLOSSY
        ):
            self.mpid = MPID.CDTRAY
            self.mlid = MLID.CDLABEL

        self._exit_packet_mode()

        # REMOTE commands
        self._remote1_enter()
        self._time_init()
        self._job_start()
        self._job_header(job_name=self.name)
        self._hardware_device()

        self._paper_path(self.mpid)
        self._duplex(self.duplex)

        self._remote1_exit()

        # ESC/P setup commands
        self._init_printer()
        self._graphics_mode()  # ESC (G
        self._set_unit(self.dpi, self.dpi, self.dpi)  # ESC (U

        # ESC/P printing method
        self._direction(pd=self.pd)  # ESC U
        self._color_mode(cm=self.cm)  # ESC (K
        self._dot_size(self.dpi)  # ESC (e
        self._image_resolution()  # ESC (D

        # ESC/P set print format
        size = self._page_format(msid=self.msid, margin=self.margin, dpi=self.dpi)
        self._paper_dimension(msid=self.msid)  # ESC (S
        self._print_method()  # ESC (m

        return size

    def _end(self):
        self._init_printer()

        self._remote1_enter()
        if self.duplex:
            self._duplex(False)

        self._job_end()
        self._remote1_exit()

    def print_pages(self, rasters: list[Image], bpp: int = 1):
        size = self._start()
        mm2in = 1.0 / 25.4

        delta_x = int(self.margin[0] * mm2in * self.dpi)
        delta_y = int(self.margin[1] * mm2in * self.dpi)

        for raster in rasters:

            self._vertical_position(y=delta_y)
            for y in range(0, min(size[1], raster.size[1])):
                for color in range(0, 4):
                    line = raster.bitline(y=y, ci=color, bpp=bpp)
                    self._horizontal_position(x=delta_x)
                    self._send_line(line=line, bpp=bpp)

                self._vertical_increment(y=1)

            self._form_feed()

        self._end()
