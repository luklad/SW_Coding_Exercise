import struct
from typing import BinaryIO

from rtsa_decoder.DSPStreamFileChunk import DSPStreamFileChunkHeader, DSPStreamFileChunk, CHUNK_HEADER_RAW_SIZE
from rtsa_decoder.DSPStreamFileChunkAntenna import DSPStreamFileChunkAntenna
from rtsa_decoder.DSPStreamFileChunkHead import DSPStreamFileChunkHead
from rtsa_decoder.DSPStreamFileChunkSamples import DSPStreamFileChunkSamples
from rtsa_decoder.DSPStreamFileChunkStreamHead import DSPStreamFileChunkStreamHead
from rtsa_decoder.DSPStreamFileChunkStreamPreview import DSPStreamFileChunkStreamPreview
from rtsa_decoder.DSPStreamFileChunkStreamTail import DSPStreamFileChunkStreamTail
from rtsa_decoder.DSPStreamFileChunkSubStream import DSPStreamFileChunkSubStream
from rtsa_decoder.DSPStreamFileChunkTail import DSPStreamFileChunkTail

chunk_id_map = {
    "DSFH": DSPStreamFileChunkHead,
    "STRM": DSPStreamFileChunkStreamHead,
    "ANTA": DSPStreamFileChunkAntenna,
    "SSTR": DSPStreamFileChunkSubStream,
    "SAMP": DSPStreamFileChunkSamples,
    "SPRV": DSPStreamFileChunkStreamPreview,
    "STRT": DSPStreamFileChunkStreamTail,
    "DSFT": DSPStreamFileChunkTail,
}


def get_chunk_object(file: BinaryIO, seek, previous):
    """
    Get a chunk object from a certain position in a file
    Args:
        file: the file object to get the chunk object from
        seek: the seek position to get the chunk object from
        previous: link to the previous chunk

    Returns:
        A chunk object already with the correct class

    """
    file.seek(seek)
    raw_header_data = file.read(CHUNK_HEADER_RAW_SIZE)
    if len(raw_header_data ) != CHUNK_HEADER_RAW_SIZE:
        return None
    data = struct.unpack('<4sIIHH', raw_header_data)
    chunk_header_data = DSPStreamFileChunkHeader(
        mChunkID=data[0].decode('ascii'),
        mChunkSize=data[1],
        mChunkFlags=data[2],
        mVersion=data[3],
        mHeaderSize=data[4],
    )
    chunk_class = chunk_id_map.get(chunk_header_data.mChunkID, None)
    if chunk_class is None:
        chunk_class = DSPStreamFileChunk

    return chunk_class(file, seek, previous, chunk_header_data)