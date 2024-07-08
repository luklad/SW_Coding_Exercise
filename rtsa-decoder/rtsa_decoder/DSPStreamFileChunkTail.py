import struct
from dataclasses import dataclass

from rtsa_decoder.DSPStreamFileChunk import DSPStreamFileChunk
from rtsa_decoder.PrintableDataclass import PrintableDataclass


@dataclass
class DSPStreamFileChunkTailHeader(PrintableDataclass):
    mCompletionTime: float
    mStreamOffset: int
    mNumStreams: int


class DSPStreamFileChunkTail(DSPStreamFileChunk):
    chunk_id = "DSFT"

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

        rawdata = self.get_header_raw_data()[:20]
        data = struct.unpack("<dqI", rawdata)

        self._header_data = DSPStreamFileChunkTailHeader(
            mCompletionTime=data[0],
            mStreamOffset=data[1],
            mNumStreams=data[2],
        )
        return self._header_data
