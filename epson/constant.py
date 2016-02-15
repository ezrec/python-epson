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

import ctypes

# Enumeration hack for Python < 
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

def clamp(minvalue, value, maxvalue):
    return ctypes.c_ubyte(max(minvalue, min(value, maxvalue))).value

# Print direction
PD = enum(BIDIREC = 0, UNIDIREC = 1, UNIDIRECT_RL = 1, AUTO = 2, UNIDIRECT_LR = 2)

# Media layout
MLID = enum(
        CUSTOM = 0,
        BORDERLESS = 1,     # 0mm borders
        BORDERS = 2,        # 3mm borders
        CDLABEL = 4,
        DIVIDE16 = 8        # 16 Division mini photo sheets
        )

# Paper path
MPID = enum('AUTO', 'REAR', 'FRONT1', 'FRONT2', 'FRONT3', 'FRONT4', 'CDTRAY', 'ROLL', 'MANUAL', 'MANUAL2')
# Autocorrection
ACT = enum(NOTHING = 0, STANDARD = 1, PIM = 2, PORTRATE = 3, VIEW = 4, NIGHTVIEW = 5)
# Red-Eye
RDE = enum(NOTHING = 0, CORRECT = 1)

# Media Size width in mm, height in mm
MSID = enum(
        A4 = (210.000,297.000),
        LETTER = (215.900,279.400),
        LEGAL = (215.900,355.600),
        A5 = (148.000,210.000),
        A6 = (105.000,148.000),
        B5 = (176.000,250.000),
        EXECUTIVE = (184.150,266.700),
        HALFLETTER = (127.000,215.900),
        PANORAMIC = (210.000,594.000),
        TRIM_4X6 = (113.600,164.400),
        _4X6 = (101.600,152.400),
        _5X8 = (127.000,203.200),
        _8X10 = (203.200,203.200),
        _10X15 = (254.000,381.000),
        _200X300 = (200.000,300.000),
        L = ( 88.900,127.000),
        POSTCARD = (100.000,148.000),
        DBLPOSTCARD = (200.000,148.000),
        ENV_10_L = (241.300,104.775),
        ENV_C6_L = (162.000,114.000),
        ENV_DL_L = (220.000,110.000),
        NEWEVN_L = (220.000,132.000),
        CHOKEI_3 = (120.000,235.000),
        CHOKEI_4 = ( 90.000,205.000),
        YOKEI_1 = (120.000,176.000),
        YOKEI_2 = (114.000,162.000),
        YOKEI_3 = ( 98.000,148.000),
        YOKEI_4 = (105.000,235.000),
        _2L = (127.000,177.800),
        ENV_10_P = (104.775,241.300),
        ENV_C6_P = (114.000,162.000),
        ENV_DL_P = (110.000,220.000),
        NEWENV_P = (132.000,220.000),
        MEISHI = ( 89.000, 55.000),
        BUZCARD_89X50 = ( 89.000, 50.000),
        CARD_54X86 = ( 54.000, 86.000),
        BUZCARD_55X91 = ( 55.000, 91.000),
        ALBUM_L = (127.000,198.000),
        ALBUM_A5 = (210.000,321.000),
        PALBUM_L_L = (127.000, 89.000),
        PALBUM_2L = (127.000,177.900),
        PALBUM_A5_L = (210.000,148.300),
        PALBUM_A4 = (210.000,296.300),
        HIVISION = (101.600,180.600),
        KAKU_2 = (240.000,332.000),
        ENV_C4_P = (229.000,324.000),
        B6 = (128.000,182.000),
        KAKU_20 = (229.000,324.000),
        A5_24HOLE = (148.000,210.000),
        A3NOBI = (329.000,483.000),
        A3 = (297.000,420.000),
        B4 = (257.000,364.000),
        USB = (279.400,431.800),
        US_11X14 = (279.400,355.600),
        B3 = (364.000,515.000),
        A2 = (420.000,594.000),
        USC = (431.800,558.800),
        US_10X12 = (254.000,304.800),
        US_12X12 = (304.800,304.800)
        )

MTID = enum(
        PLAIN = 0,
        INKJET360 = 1,
        IRON = 2,
        PHOTOINKJET = 3,
        PHOTOADSHEET = 4,
        MATTE = 5,
        PHOTO = 6,
        PHOTOFILM = 7,
        MINIPHOTO = 8,
        TRANSPARENCY = 9,
        BACKLIGHT = 10,
        PGPHOTO = 11,
        PSPHOTO = 12,
        PLPHOTO = 13,
        MCGLOSSY = 14,
        ARCHMATTE = 15,
        WATERCOLOR = 16,
        PROGLOSS = 17,
        MATTEBOARD = 18,
        PHOTOGLOSS = 19,
        SEMIPROOF = 20,
        SUPERFINE2 = 21,
        DSMATTE = 22,
        CLPHOTO = 23,
        ECOPHOTO = 24,
        VELVETFINEART = 25,
        PROOFSEMI = 26,
        HAGAKIRECL = 27,
        HAGAKIINKJET = 28,
        PHOTOINKJET2 = 29,
        DURABRITE = 30,
        MATTEMEISHI = 31,
        HAGAKIATENA = 32,
        PHOTOALBUM = 33,
        PHOTOSTAND = 34,
        RCB = 35,
        PGPHOTOEG = 24,
        ENVELOPE = 25,
        PLANTINA = 26,
        ULTRASMOOTH = 39,
        SFHAGAKI = 40,
        PHOTOSTD = 41,
        GLOSSYHAGAKI = 42,
        GLOSSYPHOTO = 43,
        GLOSSYCAST = 44,
        BUSINESSCOAT = 45,
        MEDICINEBAG = 46,
        THICKPAPER = 47,
        BROCHURE = 48,
        MATTE_DS = 49,
        BSMATTE_DS = 50,
        THREED = 51,
        LCPP = 52,
        PREPRINTED = 53,
        LETTERHEAD = 54,
        RECYCLED = 55,
        COLOR = 56,
        PLAIN_ROLL_STICKER = 59,
        GLOSSY_ROLL_STICKER = 60,
        CDDVD = 92,
        CDDVDHIGH = 92,
        CDDVDGLOSSY = 93,
        CLEANING = 99,
        UNKNOWN = 255)

MQID = enum(DRAFT = 0, NORMAL = 1, HIGH = 2)
CM = enum(COLOR = 0, MONOCHROME = 1, SEPIA = 2)
CP = enum(FULLCOLOR = 0, PALETTE = 1, JPEG = 2, PRINTCMD = 3)

CI = enum(BLACK = 0, MAGENTA = 1, CYAN = 2, YELLOW = 3,
          RED = 7, BLUE = 8, GLOSS = 9, BLACK_PHOTO = 0x40,
          K = 0, M = 1, C = 2, Y = 3, R = 7, B = 8)
#  vim: set shiftwidth=4 expandtab: # 
