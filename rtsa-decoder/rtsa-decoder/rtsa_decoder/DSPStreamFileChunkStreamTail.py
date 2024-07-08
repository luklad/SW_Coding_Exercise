import struct
from dataclasses import dataclass

from rtsa_decoder.DSPStreamFileChunk import DSPStreamFileChunk
from rtsa_decoder.PrintableDataclass import PrintableDataclass


@dataclass
class DSPStreamFileChunkStreamTailHeader(PrintableDataclass):
    mStreamOffset: int
    mSubStreamOffset: int
    mPreviewOffset: int
    mNumSamples: int
    mPayloadSize: int
    mPreviewLevels: int
    mNumPreviews: int
    mNumPreviewSegments: int
    mPadding: int
    mEndTime: float
    mAntennaOffset: int
    mMetaDataOffset: int



class DSPStreamFileChunkStreamTail(DSPStreamFileChunk):
    chunk_id = "STRT"
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

        rawdata = self.get_header_raw_data()[:80]
        data = struct.unpack("<qqqQQIIIIdqq", rawdata)

        self._header_data = DSPStreamFileChunkStreamTailHeader(
            mStreamOffset=data[0],
            mSubStreamOffset=data[1],
            mPreviewOffset=data[2],
            mNumSamples=data[3],
            mPayloadSize=data[4],
            mPreviewLevels=data[5],
            mNumPreviews=data[6],
            mNumPreviewSegments=data[7],
            mPadding=data[8],
            mEndTime=data[9],
            mAntennaOffset=data[10],
            mMetaDataOffset=data[11],
        )
        return self._header_data
