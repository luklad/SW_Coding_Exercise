"""
A draft for a rice decoder
Unknown if it works. It was not able to get reasonable values from SAMP chunks
aaronia can not provide further information on the compression so compression will not be supported anyways
"""


_offset_table = [0] * 10
for i in range(1, 9):
    _offset_table[i+1] = _offset_table[i] + (1 << (2 + 3 * (i - 1)))



def _shift_bytearray(data):
    """
    Shift a byte array by 4 bits to the left
    Args:
        data: the data to be shifted

    Returns:
        a new bytearray with the shifted data
    """
    l = len(data)
    result = bytearray(l)
    carry = 0
    for i in range(0, l):
        result[l - 1 - i] = ((data[l - 1 - i] << 4) & 0xff) + carry
        carry = data[l - 1 - i] >> 4

    return result



def _read_one(data: bytes, nibble_pointer):
    """
    Rice decode according to RTSA-FileFormat-3.pdf
    This is not very feasible in python. Should be written in c/c++ or rust
    Args:
        data: data bytes to read from
        nibble_pointer: the nibble pointer pointing to the nibble to read

    Returns:
        a tuple with the new nibble pointer and the value decoded from data
    """
    index = nibble_pointer // 2
    odd = nibble_pointer % 2 != 0

    first_byte = data[index]
    if odd:
        second_byte = 0
        if index < len(data) - 1:
            second_byte = data[index + 1]
        first_byte = ((first_byte << 4) & 0xff) + (second_byte >> 4)

    # get code length
    code_len = 1
    mask = 0x80
    while mask & first_byte == 0 and mask != 0:
        code_len += 1
        mask = mask >> 1


    bytes_to_get = (code_len + (nibble_pointer % 2)) // 2 + 1

    raw_value = data[index: index + bytes_to_get]

    # check if the data is still in range
    if len(raw_value) != bytes_to_get:
        # Todo: throw an error
        print("does not fit")
        return nibble_pointer + code_len, None

    # shift the bytearray if the lower significant nibble is the first nibble
    if odd:
        raw_value = _shift_bytearray(raw_value)

    # build the integer from the single bytes
    raw_int_value = 0
    for i in range(0, bytes_to_get):
        raw_int_value += raw_value[bytes_to_get - i - 1] << (8 * i)

    # when the code length is odd shift the integer 4 bits to the right
    if code_len % 2 == 1:
        raw_int_value = raw_int_value >> 4

    # get the sign from bit 0
    sign = raw_int_value & 0x1

    # shift out the sign bit
    raw_int_value = raw_int_value >> 1

    # mask out the leading code_length
    mask = (1 << (2 + (3 * (code_len - 1)))) - 1
    raw_int_value = raw_int_value & mask

    # add the offset
    value = raw_int_value + _offset_table[code_len]

    if (sign):
        value = value * -1

    return nibble_pointer + code_len, value


def rice_decode(data: bytes):
    """
    Rice Decode a bytearray to a list of integer values
    Args:
        data:
            byte array to decode

    Returns:
        a list of decoded integer values
    """
    print(len(data))
    nibbles_len = len(data) * 2
    nibble_pointer = 0
    values = []
    while nibble_pointer < nibbles_len:
        (nibble_pointer, value) = _read_one(data, nibble_pointer)
        values.append(value)
    print(len(values))
    return values
