import struct
from dataclasses import dataclass
from typing import List

from rtsa_decoder.DSPStreamFileChunk import DSPStreamFileChunk
from rtsa_decoder.PrintableDataclass import PrintableDataclass


@dataclass
class DSPStreamFileChunkAntennaHeader(PrintableDataclass):
    mAntennaID: int
    mAntennaOffset: float
    mName: str
    mLatitude: float
    mLongitude: float
    mFlags: int
    mNumSegments: int
    mTransform: List[float]
    mAntennaUUID: str


class DSPStreamFileChunkAntenna(DSPStreamFileChunk):
    chunk_id = "ANTA"
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

        rawdata = self.get_header_raw_data()[:248]
        data = struct.unpack("<Qq128sddII64s16s", rawdata)
        transform = list(struct.unpack("<16f", data[7]))
        name_end_index = data[2].find(b'\x00')
        uuid_end_index = data[8].find(b'\x00')
        self._header_data = DSPStreamFileChunkAntennaHeader(
            mAntennaID=data[0],
            mAntennaOffset=data[1],
            mName=data[2][:name_end_index].decode('ascii'),
            mLatitude=data[3],
            mLongitude=data[4],
            mFlags=data[5],
            mNumSegments=data[6],
            mTransform=transform,
            mAntennaUUID=data[8][:uuid_end_index].decode('ascii'),
        )
        return self._header_data
