import struct
from dataclasses import dataclass

from rtsa_decoder.DSPStreamFileChunk import DSPStreamFileChunk
from rtsa_decoder.PrintableDataclass import PrintableDataclass


@dataclass
class DSPStreamFileChunkStreamHeadHeader(PrintableDataclass):
    mStreamID: int
    mStartTime: float
    mStreamOffset: int
    mStreamPadding: int


class DSPStreamFileChunkStreamHead(DSPStreamFileChunk):
    chunk_id = "STRM"
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
        data = struct.unpack("<Qdqq", rawdata)

        self._header_data = DSPStreamFileChunkStreamHeadHeader(
            mStreamID=data[0],
            mStartTime=data[1],
            mStreamOffset=data[2],
            mStreamPadding=data[3]
        )
        return self._header_data

    def get_first_sub_stream(self):
        """
        Get the first sub stream in a stream
        Returns:
            A sub stream object

        """
        obj = self
        while True:
            obj = obj.get_next_chunk()
            if obj is None:
                return None
            chunk_id = obj.get_chunk_header_data().mChunkID
            if chunk_id == "SSTR":
                return obj
            if chunk_id == "STRT":
                return None