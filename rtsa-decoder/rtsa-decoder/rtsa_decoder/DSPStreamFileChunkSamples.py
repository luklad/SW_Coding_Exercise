import enum
import struct
from dataclasses import dataclass
import numpy as np

from rtsa_decoder.DSPStreamFileChunk import DSPStreamFileChunk
from rtsa_decoder.PrintableDataclass import PrintableDataclass
from rtsa_decoder.RTSADecoderException import RTSADecoderException


class DSPStreamSampleType(enum.IntEnum):
    DSST_U8 = 0
    DSST_U16 = 1
    DSST_S16 = 2
    DSST_U32 = 3
    DSST_S32 = 4
    DSST_F32 = 5
    DSST_U8N = 6
    DSST_U16N = 7
    DSST_S16N = 8
    DSST_U32N = 9
    DSST_S32N = 10
    DSST_F32N = 11


class DSPStreamPayloadType(enum.IntEnum):
    DSPT_GENERIC = 0
    DSPT_AUDIO = 1
    DSPT_IQ = 2
    DSPT_SPECRTA = 3
    DSPT_DETECTION = 4
    DSPT_HISTOGRAM = 5
    DSPT_ENERGY = 6
    DSPT_VECTOR3 = 7
    DSPT_STRUCTURED = 8
    DSPT_IQ_SLICE = 9
    DSPT_IMAGE = 10


@dataclass
class DSPStreamFileChunkSamplesHeader(PrintableDataclass):
    mStreamID: int
    mSubStreamID: int
    mSampleType: DSPStreamSampleType
    mSampleUnit: int
    mPayloadType: int
    mCompression: int
    mPacketStartTime: float
    mPacketEndTime: float
    mPacketFlags: int
    mSampleSize: int
    mSampleDepth: int
    mNumSamples: int


class DSPStreamFileChunkSamples(DSPStreamFileChunk):
    chunk_id = "SAMP"
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

        rawdata = self.get_header_raw_data()[:48]
        data = struct.unpack("<QIBBBBddIIII", rawdata)
        self._header_data = DSPStreamFileChunkSamplesHeader(
            mStreamID=data[0],
            mSubStreamID=data[1],
            mSampleType=data[2],
            mSampleUnit=data[3],
            mPayloadType=data[4],
            mCompression=data[5],
            mPacketStartTime=data[6],
            mPacketEndTime=data[7],
            mPacketFlags=data[8],
            mSampleSize=data[9],
            mSampleDepth=data[10],
            mNumSamples=data[11],
        )
        return self._header_data

    def read_into_array(self, arr, pointer):
        payload = self.get_payload_raw_data()
        header_data = self.get_header_data()
        sample_size = header_data.mSampleSize
        if len(payload) != header_data.mSampleSize * 4:
            raise RTSADecoderException(f"get_samples_array: Length of payload and sample size do not match"
                                       f" (at position {self.get_seek()})")
        if header_data.mSampleType != DSPStreamSampleType.DSST_F32:
            raise RTSADecoderException(f"get_samples_array: Only DDST_F32 is supported as sample type"
                                       f" (at position {self.get_seek()})")
        if header_data.mPayloadType != DSPStreamPayloadType.DSPT_SPECRTA:
            raise RTSADecoderException(f"get_samples_array: Only DSPT_SPECRTA is currently supported as payload type "
                                       f"(at position {self.get_seek()}")
        if header_data.mCompression != 0:
            raise RTSADecoderException(f"get_samples_array: Compression is not supported "
                                       f"(at position {self.get_seek()}")

        arr[pointer:pointer + sample_size] = np.frombuffer(payload, dtype=np.float32)
        return pointer + sample_size








