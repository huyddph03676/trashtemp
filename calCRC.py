# -*- coding: utf-8 -*-
import struct, sys, minimalmodbus, serial
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

_CRC16TABLE = (
        0, 49345, 49537,   320, 49921,   960,   640, 49729, 50689,  1728,  1920,
    51009,  1280, 50625, 50305,  1088, 52225,  3264,  3456, 52545,  3840, 53185,
    52865,  3648,  2560, 51905, 52097,  2880, 51457,  2496,  2176, 51265, 55297,
     6336,  6528, 55617,  6912, 56257, 55937,  6720,  7680, 57025, 57217,  8000,
    56577,  7616,  7296, 56385,  5120, 54465, 54657,  5440, 55041,  6080,  5760,
    54849, 53761,  4800,  4992, 54081,  4352, 53697, 53377,  4160, 61441, 12480,
    12672, 61761, 13056, 62401, 62081, 12864, 13824, 63169, 63361, 14144, 62721,
    13760, 13440, 62529, 15360, 64705, 64897, 15680, 65281, 16320, 16000, 65089,
    64001, 15040, 15232, 64321, 14592, 63937, 63617, 14400, 10240, 59585, 59777,
    10560, 60161, 11200, 10880, 59969, 60929, 11968, 12160, 61249, 11520, 60865,
    60545, 11328, 58369,  9408,  9600, 58689,  9984, 59329, 59009,  9792,  8704,
    58049, 58241,  9024, 57601,  8640,  8320, 57409, 40961, 24768, 24960, 41281,
    25344, 41921, 41601, 25152, 26112, 42689, 42881, 26432, 42241, 26048, 25728,
    42049, 27648, 44225, 44417, 27968, 44801, 28608, 28288, 44609, 43521, 27328,
    27520, 43841, 26880, 43457, 43137, 26688, 30720, 47297, 47489, 31040, 47873,
    31680, 31360, 47681, 48641, 32448, 32640, 48961, 32000, 48577, 48257, 31808,
    46081, 29888, 30080, 46401, 30464, 47041, 46721, 30272, 29184, 45761, 45953,
    29504, 45313, 29120, 28800, 45121, 20480, 37057, 37249, 20800, 37633, 21440,
    21120, 37441, 38401, 22208, 22400, 38721, 21760, 38337, 38017, 21568, 39937,
    23744, 23936, 40257, 24320, 40897, 40577, 24128, 23040, 39617, 39809, 23360,
    39169, 22976, 22656, 38977, 34817, 18624, 18816, 35137, 19200, 35777, 35457,
    19008, 19968, 36545, 36737, 20288, 36097, 19904, 19584, 35905, 17408, 33985,
    34177, 17728, 34561, 18368, 18048, 34369, 33281, 17088, 17280, 33601, 16640,
    33217, 32897, 16448)

def validator(instance):
    '''Decode raw data from register'''
    if instance:

        decoder = BinaryPayloadDecoder.fromRegisters(
            instance,
            byteorder=Endian.Big, wordorder=Endian.Little
        )
        return float(decoder.decode_32bit_float())

    else:
        # Error handling.
        print("Registers Reading Error!, Try again.")
        return None

def _pack(formatstring, value):
    """Pack a value into a bytestring.

    Uses the built-in :mod:`struct` Python module.

    Args:
        * formatstring (str): String for the packing. See the :mod:`struct` module for details.
        * value (depends on formatstring): The value to be packed

    Returns:
        A bytestring (str).

    Raises:
        ValueError

    Note that the :mod:`struct` module produces byte buffers for Python3,
    but bytestrings for Python2. This is compensated for automatically.

    """

    try:
        result = struct.pack(formatstring, value)
    except:
        errortext = 'The value to send is probably out of range, as the num-to-bytestring conversion failed.'
        errortext += ' Value: {0!r} Struct format code is: {1}'
        raise ValueError(errortext.format(value, formatstring))

    if sys.version_info[0] > 2:
        return str(result, encoding='latin1')  # Convert types to make it Python3 compatible
    return result

def _unpack(formatstring, packed):
    """Unpack a bytestring into a value.

    Uses the built-in :mod:`struct` Python module.

    Args:
        * formatstring (str): String for the packing. See the :mod:`struct` module for details.
        * packed (str): The bytestring to be unpacked.

    Returns:
        A value. The type depends on the formatstring.

    Raises:
        ValueError

    Note that the :mod:`struct` module wants byte buffers for Python3,
    but bytestrings for Python2. This is compensated for automatically.

    """

    if sys.version_info[0] > 2:
        packed = bytes(packed, encoding='latin1')  # Convert types to make it Python3 compatible

    try:
        value = struct.unpack(formatstring, packed)[0]
    except:
        errortext = 'The received bytestring is probably wrong, as the bytestring-to-num conversion failed.'
        errortext += ' Bytestring: {0!r} Struct format code is: {1}'
        raise ValueError(errortext.format(packed, formatstring))

    return value

def _numToOneByteString(inputvalue):
    """Convert a numerical value to a one-byte string.

    Args:
        inputvalue (int): The value to be converted. Should be >=0 and <=255.

    Returns:
        A one-byte string created by chr(inputvalue).

    Raises:
        TypeError, ValueError

    """

    return chr(inputvalue)

def _numToTwoByteString(value, numberOfDecimals=0, LsbFirst=False, signed=False):
    """Convert a numerical value to a two-byte string, possibly scaling it.

    Args:
        * value (float or int): The numerical value to be converted.
        * numberOfDecimals (int): Number of decimals, 0 or more, for scaling.
        * LsbFirst (bol): Whether the least significant byte should be first in the resulting string.
        * signed (bol): Whether negative values should be accepted.

    Returns:
        A two-byte string.

    Raises:
        TypeError, ValueError. Gives DeprecationWarning instead of ValueError
        for some values in Python 2.6.

    Use ``numberOfDecimals=1`` to multiply ``value`` by 10 before sending it to the slave register.
    Similarly ``numberOfDecimals=2`` will multiply ``value`` by 100 before sending it to the slave register.

    Use the parameter ``signed=True`` if making a bytestring that can hold
    negative values. Then negative input will be automatically converted into
    upper range data (two's complement).

    The byte order is controlled by the ``LsbFirst`` parameter, as seen here:

    ====================== ============= ====================================
    ``LsbFirst`` parameter Endianness    Description
    ====================== ============= ====================================
    False (default)        Big-endian    Most significant byte is sent first
    True                   Little-endian Least significant byte is sent first
    ====================== ============= ====================================

    For example:
        To store for example value=77.0, use ``numberOfDecimals = 1`` if the register will hold it as 770 internally.
        The value 770 (dec) is 0302 (hex), where the most significant byte is 03 (hex) and the
        least significant byte is 02 (hex). With ``LsbFirst = False``, the most significant byte is given first
        why the resulting string is ``\\x03\\x02``, which has the length 2.

    """

    multiplier = 10 ** numberOfDecimals
    integer = int(float(value) * multiplier)

    if LsbFirst:
        formatcode = '<'  # Little-endian
    else:
        formatcode = '>'  # Big-endian
    if signed:
        formatcode += 'h'  # (Signed) short (2 bytes)
    else:
        formatcode += 'H'  # Unsigned short (2 bytes)

    outstring = _pack(formatcode, integer)
    assert len(outstring) == 2
    return outstring

def _calculateCrcString(inputstring):
    """Calculate CRC-16 for Modbus.

    Args:
        inputstring (str): An arbitrary-length message (without the CRC).

    Returns:
        A two-byte CRC string, where the least significant byte is first.

    """

    # Preload a 16-bit register with ones
    register = 0xFFFF

    for char in inputstring:
        register = (register >> 8) ^ _CRC16TABLE[(register ^ ord(char)) & 0xFF]
    return _numToTwoByteString(register, LsbFirst=True)

def shex2dec(s=''):
    s = s.upper()
    r = '123456789ABCDEF'
    try:
        if len(s) == 1:
            return r.index(s) + 1
        elif s == '':
            return 0
        else:
            first = (r.index(s[0])+1)* 16**(len(s)-1)
            return first + shex2dec(s[1:])
    except:
        return None

def getList(shex):
    shex = shex.replace(" ", "")
    return [shex2dec(shex[6:10]), shex2dec(shex[10:14])]

def payloadbuild(idsl, fc, register, number):
    firstPart = _numToOneByteString(idsl) + _numToOneByteString(fc)
    secPart = _numToTwoByteString(register) + _numToTwoByteString(number)
    part01 = firstPart + secPart

    request = part01 + _calculateCrcString(part01)
    # bytes(request, encoding='latin1')
    return request

print(bytes(payloadbuild(3, 3, 3926, 2), encoding='latin1')) # generate modbus request
hexcode = minimalmodbus._hexlify(payloadbuild(3, 3, 3926, 2)) # convert bytes respone to hex
print(hexcode)

print(bytes(payloadbuild(3, 3, 3914, 2), encoding='latin1'))
print(minimalmodbus._hexlify(payloadbuild(3, 3, 3914, 2)))
