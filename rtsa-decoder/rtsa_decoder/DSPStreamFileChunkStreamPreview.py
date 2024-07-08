import struct
from dataclasses import dataclass
from typing import List

from rtsa_decoder.DSPStreamFileChunk import DSPStreamFileChunk
from rtsa_decoder.PrintableDataclass import PrintableDataclass


@dataclass
class DSPStreamFileChunkStreamPreviewHeader(PrintableDataclass):
    HistogramWidth = 48
    HistogramHeight = 32
    WaterfallWidth = 128
    SegmentsShift = 4
    Segments = 16
    Samples = 4096

    mPreviewLevel: int
    mPreviewCount: int
    mPreviewPadding1: int
    mPreviewPadding2: int
    mPreviewOffsets: List[int]
    mPreviewTimes: List[float]
    mPreviewSamples: List[float]


class DSPStreamFileChunkStreamPreview(DSPStreamFileChunk):
    chunk_id = "SPRV"
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

        rawdata = self.get_header_raw_data()[:392]
        segments = DSPStreamFileChunkStreamPreviewHeader.Segments
        segments_len = segments * 8
        data = struct.unpack(f"<BBHI{segments_len}s{segments_len}s{segments_len}s", rawdata)
        m_preview_offsets = list(struct.unpack(f"<{segments}q", data[4]))
        m_preview_times = list(struct.unpack(f"<{segments}d", data[5]))
        m_preview_samples = list(struct.unpack(f"<{segments}Q", data[6]))

        self._header_data = DSPStreamFileChunkStreamPreviewHeader(
            mPreviewLevel=data[0],
            mPreviewCount=data[1],
            mPreviewPadding1=data[2],
            mPreviewPadding2=data[3],
            mPreviewOffsets=m_preview_offsets,
            mPreviewTimes=m_preview_times,
            mPreviewSamples=m_preview_samples,
        )
        return self._header_data
