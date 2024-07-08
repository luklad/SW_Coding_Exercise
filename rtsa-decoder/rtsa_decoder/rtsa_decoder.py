from dataclasses import dataclass
import numpy as np


from rtsa_decoder.DSPStreamFileChunkStreamHead import DSPStreamFileChunkStreamHead
from rtsa_decoder.DSPStreamFileChunkSubStream import DSPStreamFileChunkSubStream
from rtsa_decoder.chunk_id_map import get_chunk_object


@dataclass
class SamplesFromFileResult:
    samples: np.ndarray
    stream_start_time: float
    samples_start_time: float
    samples_end_time: float
    start_time: float
    end_time: float
    frequency_start: float
    frequency_step: float
    frequency_span: float


def get_samples_from_file(file_object):
    file_header = get_chunk_object(file_object, 0, None)
    stream_head: DSPStreamFileChunkStreamHead = file_header.get_first_stream()
    stream_head_header_data = stream_head.get_header_data()
    sub_stream: DSPStreamFileChunkSubStream = stream_head.get_first_sub_stream()
    sub_stream_header_data = sub_stream.get_header_data()

    stream_start_time = stream_head_header_data.mStartTime
    frequency_start = sub_stream_header_data.mFrequencyStart
    frequeny_step = sub_stream_header_data.mFrequencyStep
    frequency_span = sub_stream_header_data.mFrequencySpan

    sample_data = sub_stream.get_samples_array()

    samples = sample_data.samples
    samples_start_time = sample_data.start_time
    samples_end_time = sample_data.end_time

    start_time = stream_start_time + samples_start_time
    end_time = stream_start_time + samples_end_time

    return SamplesFromFileResult(
        samples=samples,
        stream_start_time=stream_start_time,
        samples_start_time=samples_start_time,
        samples_end_time=samples_end_time,
        start_time=start_time,
        end_time=end_time,
        frequency_start=frequency_start,
        frequency_step=frequeny_step,
        frequency_span=frequency_span,
    )
