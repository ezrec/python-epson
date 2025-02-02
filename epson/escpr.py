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

import math
import struct
import epson
import epson.escp

from epson.constant import *


class Interface(epson.escp.Interface):
    """Base class for accessing EPSON ESC/P Raster printers"""

    # ESC/P-R mode
    ESCPRMode = b"\x1b(R\x06\x00\x00ESCPR"
    # ESC/P-R JPEG mode
    ESCPRModeJpg = b"\x1b(R\x07\x00\x00ESCPRJ"

    def __init__(self, io=None):
        """Initialize class"""
        super(Interface, self).__init__(io=io)

    """ ESC/P Raster Mode """

    def _raster_enter(self, jpeg=False):
        if jpeg:
            self._send(self.ESCPRModeJpg)
        else:
            self._send(self.ESCPRMode)

    """ Raster Mode command wrappers """

    def _raster_cmd(self, cmd, code, data=None):
        if data is None:
            data = b""
        self._send(b"\x1b" + cmd + struct.pack("<L", len(data)) + code + data)

    def _raster_quality(
        self,
        mtid=MTID.PLAIN,
        mqid=MQID.DRAFT,
        cm=CM.COLOR,
        brightness=0,
        contrast=0,
        saturation=0,
        cp=CP.FULLCOLOR,
        palette=None,
    ):
        if palette is None:
            palette = b""

        data = (
            byte(mtid)
            + byte(mqid)
            + byte(cm)
            + byte(clamp(-50, brightness, 50))
            + byte(clamp(-50, contrast, 50))
            + byte(clamp(-50, saturation, 50))
            + byte(cp)
            + struct.pack(">H", len(palette))
            + palette
        )
        self._raster_cmd(b"q", b"setq", data)

    def _raster_check(self):
        # Only needed on 'version 3' or higher printers?
        # self._raster_cmd("u", "chku", "\x01\x01")
        pass

    def _raster_job(
        self,
        paper=MSID.LETTER,
        mlid=MLID.BORDERLESS,
        margin=(0, 0, 0, 0),
        dpi=720,
        pd=PD.BIDIREC,
    ):
        ir = 0
        if dpi == 720:
            ir = 1
        elif dpi == 300:
            ir = 2
        elif dpi == 600:
            ir = 3
        elif dpi == 360:
            ir = 0
        else:
            dpi = 360
            ir = 0

        if mlid == MLID.BORDERLESS:
            margin = (0, 0, 0, 0)

        mm2in = 1.0 / 25.4
        paperWidth = math.ceil(paper[0] * mm2in * dpi)
        paperHeight = math.ceil(paper[1] * mm2in * dpi)
        marginLeft = math.floor(margin[0] * mm2in * dpi)
        marginTop = math.floor(margin[1] * mm2in * dpi)
        marginRight = math.floor(margin[2] * mm2in * dpi)
        marginBottom = math.floor(margin[3] * mm2in * dpi)
        printableWidth = paperWidth - marginLeft - marginRight
        printableHeight = paperHeight - marginTop - marginBottom
        data = struct.pack(
            ">LLHHLLBB",
            paperWidth,
            paperHeight,
            marginTop,
            marginLeft,
            printableWidth,
            printableHeight,
            ir,
            pd,
        )

        self._raster_cmd(b"j", b"setj", data)
        return (printableWidth, printableHeight)

    def _jpeg_auto_photo_fix(
        self, cm=CM.COLOR, act=ACT.NOTHING, sharpness=0, rde=RDE.NOTHING
    ):
        data = byte(cm) + byte(act) + byte(clamp(-50, sharpness, 50)) + byte(rde)
        self._raster_cmd(b"a", b"seta", data)

    def _jpeg_copies(self, copies=1):
        data = byte(clamp(1, copies, 255))
        self._raster_cmd(b"c", b"setc", data)

    def _jpeg_job(self):
        # TODO: Add JPEG page size support
        pass

    def _jpeg_size(
        self, mlid=MLID.BORDERLESS, pd=PD.BIDIREC, cddim_id=None, cddim_od=None
    ):
        data = byte(99)  # Custom size - always send _raster_job before this!

        # Media layout
        if mlid == MLID.BORDERLESS:
            data += byte(0x01)
        elif mlid == MLID.CDLABEL:
            data += byte(0x09)
        elif mlid == MLID.DIVIDE16:
            data += byte(0x90)
        else:
            data += byte(0)

        if cddim_id is None:
            cddim_id = 43

        if cddim_od is None:
            cddim_od = 116

        data += byte(clamp(18, cddim_id, 46))
        data += byte(clamp(114, cddim_od, 120))
        date += byte(pd)

        self._raster_cmd(b"j", b"sets", data)

    def _raster_start_page(self):
        self._raster_cmd(b"p", b"sttp")

    def _raster_printnum2(self, pageno=1):
        self._raster_cmd(b"p", b"setn", byte(pageno))

    def _send_jpeg(self, chunk):
        while len(chunk) > 0:
            size = len(chunk)
            if size > 0xFFFF:
                size = 0xFFFF
            self._raster_cmd(b"d", b"jsnd", struct.pack(">H", size) + chunk[0:size])
            chunk = chunk[size:]

    def _send_line(self, line=None, offset=(0, 0), compress=False):
        if compress:
            line = epson.escpr.run_length_encode(line, 3)
            cmode = 1
        else:
            cmode = 0

        data = struct.pack(">HHBH", offset[0], offset[1], cmode, len(line))

        self._raster_cmd(b"d", b"dsnd", data + line)

    def _raster_endpage(self, pages_remaining=0):
        self._raster_cmd(b"p", b"endp", byte(pages_remaining))

    def _raster_endjob(self):
        self._raster_cmd(b"j", b"endj")


class Job(Interface):
    """EPSON ESC/P Raster Job Wrapper"""

    def __init__(self, io=None, name="ESCPRLib"):
        super(Job, self).__init__(io=io)

        # Job name
        self.name = name

        # Output selection
        self.dpi = 360
        self.pd = PD.BIDIREC

        # Paper path
        self.mpid = MPID.REAR
        self.duplex = False

        self.cm = CM.COLOR

        # JPEG auto photo fix
        self.act = ACT.NOTHING
        self.sharpness = 0
        self.rde = RDE.NOTHING

        # Quality settings
        self.mqid = MQID.HIGH
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
        self._init_printer()

        # REMOTE commands
        self._remote1_enter()
        self._time_init()
        self._job_start()
        self._job_header(job_name=self.name)
        self._hardware_device()

        self._paper_path(self.mpid)
        self._duplex(self.duplex)

        self._remote1_exit()

        # ESC/P Raster commands
        self._raster_enter(jpeg=(self.cp == CP.JPEG))

        self._raster_quality(
            mtid=self.mtid,
            mqid=self.mqid,
            cm=self.cm,
            brightness=self.brightness,
            contrast=self.contrast,
            saturation=self.saturation,
            cp=self.cp,
            palette=self.palette,
        )

        if self.cp != CP.JPEG:
            self._raster_check()

            size = self._raster_job(
                paper=self.msid,
                mlid=self.mlid,
                margin=self.margin,
                dpi=self.dpi,
                pd=self.pd,
            )

        else:
            self._jpeg_auto_photo_fix(
                cm=self.cm, act=self.act, sharpness=self.sharpness, rde=self.rde
            )
            if copies > 1:
                self._jpeg_copies(copies=copies)

            size = self._raster_job(
                paper=self.msid,
                mlid=self.mlid,
                margin=self.margin,
                dpi=self.dpi,
                pd=self.pd,
            )

            self._jpeg_size(
                mlid=self.mlid,
                pd=self.pd,
                cddim_id=self.cddim_id,
                cddim_od=self.cddim_od,
            )

        return size

    def _end(self):
        self._raster_endjob()

        self._init_printer()

        self._remote1_enter()

        self._load_defaults()
        self._job_end()

        self._remote1_exit()

    def print_pages(self, rasters=None, copies=1):

        size = self._start(copies=copies)

        for page in range(1, len(rasters) + 1):
            raster = rasters[page - 1]

            self._raster_start_page()
            if page < 99:
                self._raster_printnum2(page)
            else:
                self._raster_printnum2(99)

            for y in range(0, min(size[1], raster.size[1])):
                self._send_line(line=raster.line(y), offset=(0, y), compress=True)

            rpage = len(rasters) - page
            if rpage > 99:
                rpage = 99
            self._raster_endpage(pages_remaining=rpage)

        self._end()
