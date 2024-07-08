import importlib
from dataclasses import dataclass, fields
from typing import Optional, BinaryIO

from rtsa_decoder.PrintableDataclass import PrintableDataclass


@dataclass
class DSPStreamFileChunkHeader(PrintableDataclass):
    mChunkID: str
    mChunkSize: int
    mChunkFlags: int
    mVersion: int
    mHeaderSize: int


CHUNK_HEADER_RAW_SIZE = 16

_imported_get_chunk_object = None


def get_chunk_object(file: BinaryIO, seek, previous):
    """
    Wrapper to resolve circular import (dont know if there is a better way)
    Args:
        file: the file to find the chunk object in
        seek: the position to find the chunk object
        previous: the previous chunk object (if available)

    Returns:
        a descendant of DSPStreamFileChunk

    """
    global _imported_get_chunk_object
    if _imported_get_chunk_object is None:
        _imported_get_chunk_object = importlib.import_module('rtsa_decoder.chunk_id_map').get_chunk_object
    return _imported_get_chunk_object(file, seek, previous)


class DSPStreamFileChunk(object):
    def __init__(self, file, seek, previous, chunk_header_data):
        """
        Args:
            file: the file object
            seek: the seek position at the start of the chunk
            previous: link to the previous chunk object
            chunk_header_data: already extracted chunk header data
        """
        super(DSPStreamFileChunk, self).__init__()
        self._file = file
        self._seek = seek
        self._previous = previous

        self._chunk_header_data: Optional[DSPStreamFileChunkHeader] = chunk_header_data

    def get_chunk_header_data(self):
        return self._chunk_header_data

    def get_header_raw_data(self):
        header_size = self._chunk_header_data.mHeaderSize
        length = header_size - CHUNK_HEADER_RAW_SIZE
        self._file.seek(self._seek + CHUNK_HEADER_RAW_SIZE)
        return self._file.read(length)

    def get_payload_raw_data(self):
        header_size = self._chunk_header_data.mHeaderSize
        self._file.seek(self._seek + header_size)
        length = self._chunk_header_data.mChunkSize - header_size
        return self._file.read(length)

    def get_next_chunk_seek(self):
        return self._seek + self._chunk_header_data.mChunkSize

    def get_next_chunk(self):
        return get_chunk_object(self._file, self._seek + self._chunk_header_data.mChunkSize, self)

    def get_header_data(self):
        return None

    def get_seek(self):
        return self._seek
