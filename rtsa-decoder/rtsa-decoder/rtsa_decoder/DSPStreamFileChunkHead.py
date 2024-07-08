import struct
from dataclasses import dataclass

from rtsa_decoder.DSPStreamFileChunk import DSPStreamFileChunk
from datetime import datetime

from rtsa_decoder.PrintableDataclass import PrintableDataclass


@dataclass
class DSPStreamFileChunkHeadHeader(PrintableDataclass):
    mCreationTime: datetime


class DSPStreamFileChunkHead(DSPStreamFileChunk):
    chunk_id = "DSFH"

    def __init__(self, file, seek, previous, chunk_header_data):
        """
        Args:
            file: the file object
            seek: the seek position at the start of the chunk
            previous: link to the previous chunk object
            chunk_header_data: already extracted chunk header data
        """
        super().__init__(file, seek, previous, chunk_header_data)
        self._header_data = None

    def get_header_data(self):
        if self._header_data is not None:
            return self._header_data

        rawdata = self.get_header_raw_data()
        data = struct.unpack("<d", rawdata)

        self._header_data = DSPStreamFileChunkHeadHeader(
            mCreationTime=datetime.utcfromtimestamp(data[0] / 1000000)
        )
        return self._header_data

    def get_first_stream(self):
        """
        Get the first stream in a file
        Returns:
            A stream head object

        """
        obj = self
        while True:
            obj = obj.get_next_chunk()
            if obj is None:
                return None
            chunk_id = obj.get_chunk_header_data().mChunkID
            if chunk_id == "STRM":
                return obj
            if chunk_id == "DSFT":
                return None


