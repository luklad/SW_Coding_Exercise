import struct
from dataclasses import dataclass
from typing import Any

import numpy as np

from rtsa_decoder.DSPStreamFileChunk import DSPStreamFileChunk
from rtsa_decoder.PrintableDataclass import PrintableDataclass


@dataclass
class DSPStreamFileChunkSubStreamHeader(PrintableDataclass):
    mStreamID: int
    mSubStreamID: int
    mSubStreamOffset: int
    mFrequencyStart: float
    mFrequencyStep: float
    mFrequencySpan: float
    mValueMinimum: float
    mValueMaximum: float
    mDirection: float
    mAntennaIndex: int
    mNumCategories: int
    mName: str
    mAntennaID: int
    mMetaDataID: int


@dataclass
class SubStreamSamplesResult:
    samples: np.ndarray
    start_time: float
    end_time: float


class DSPStreamFileChunkSubStream(DSPStreamFileChunk):
    chunk_id = "SSTR"

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

        rawdata = self.get_header_raw_data()[:224]
        data = struct.unpack("<QQqddddddII128sQQ", rawdata)
        name_end_index = data[11].find(b'\x00')
        self._header_data = DSPStreamFileChunkSubStreamHeader(
            mStreamID=data[0],
            mSubStreamID=data[1],
            mSubStreamOffset=data[2],
            mFrequencyStart=data[3],
            mFrequencyStep=data[4],
            mFrequencySpan=data[5],
            mValueMinimum=data[6],
            mValueMaximum=data[7],
            mDirection=data[8],
            mAntennaIndex=data[9],
            mNumCategories=data[10],
            mName=data[11][:name_end_index].decode('ascii'),
            mAntennaID=data[12],
            mMetaDataID=data[13],
        )
        return self._header_data

    def get_samples_array(self):
        """
        Get a numpy float array of samples and organize them in sweeps. Also get the start and end time of the samples
        Returns:
            a two-dimensional numpy array with samples
        """
        header_data = self.get_header_data()
        sweep_samples = round(header_data.mFrequencySpan / header_data.mFrequencyStep)
        stream_id = header_data.mStreamID
        sub_stream_id = header_data.mSubStreamID

        finished = False
        obj = self
        sample_chunks = []
        while not finished:
            obj = obj.get_next_chunk()
            if obj is None:
                # TODO: issue a warning here or throw exception?
                finished = True
            chunk_id = obj.get_chunk_header_data().mChunkID
            if chunk_id == "SAMP":
                sample_data = obj.get_header_data()
                if sample_data.mStreamID == stream_id and sample_data.mSubStreamID == sub_stream_id:
                    sample_chunks.append(obj)
            if chunk_id == "STRT":
                finished = True

        start_time = sample_chunks[0].get_header_data().mPacketStartTime
        end_time = sample_chunks[-1].get_header_data().mPacketEndTime

        # get total size to initialize a numpy array
        num_samples = 0
        for chunk in sample_chunks:
            sample_data = chunk.get_header_data()
            num_samples += sample_data.mSampleSize

        result = np.empty(num_samples, dtype=np.float32)

        print(f"get_samples_array: Number of samples: {num_samples}")
        print(f"get_samples_array: Number of sweeps: {num_samples / sweep_samples}")

        pointer = 0
        for chunk in sample_chunks:
            pointer = chunk.read_into_array(result, pointer)

        rows = num_samples // sweep_samples

        result = result.reshape(rows, sweep_samples)

        return SubStreamSamplesResult(
            samples=result,
            start_time=start_time,
            end_time=end_time,
        )
