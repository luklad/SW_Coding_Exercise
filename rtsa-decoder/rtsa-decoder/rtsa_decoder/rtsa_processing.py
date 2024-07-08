import json
from datetime import datetime
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np

from rtsa_decoder.rtsa_decoder import SamplesFromFileResult

def get_heatmap_png(data: SamplesFromFileResult):
    """
    Get a heatmap of the recorded spectrum as png
    Args:
        data: the sample data with metadata

    Returns:
        a bytearray which can be saved as png
    """
    plt.switch_backend('Agg')
    plt.clf()
    plt.xlabel('Frequency [MHz]')
    frequency_steps = data.samples.shape[1]
    xticks = np.linspace(0, frequency_steps, 10)
    xticks_labels = list(np.linspace(data.frequency_start / 1e6, (data.frequency_start + data.frequency_span) / 1e6, 10))
    xticks_labels = [f"{l:.1f}" for l in xticks_labels]
    yticks = np.linspace(0, data.samples.shape[0], 10)
    yticks_labels = list(np.linspace(data.samples_start_time, data.samples_end_time,10))
    yticks_labels = [f"{l:.1f}" for l in yticks_labels]
    plt.xticks(xticks, xticks_labels)
    plt.yticks(yticks, yticks_labels)
    plt.ylabel('Time [s]')
    plt.title(datetime.utcfromtimestamp(data.stream_start_time))
    plt.imshow(data.samples, cmap='gnuplot2', aspect='auto')
    result = BytesIO()
    plt.savefig(result, format="png")

    return result.getvalue()


def get_max_hold_json(data: SamplesFromFileResult):
    """
    Write a downsampled max hold json
    Same could be done for csv
    Args:
        data:
            sample data with metadata

    Returns:
        an utf8 string with the json data
    """
    max_hold: np.ndarray = np.amax(data.samples, axis=0)

    # assumption is the array is dividable by 1000
    downsampled_max_hold = max_hold.reshape(-1, len(max_hold) // 1000).mean(axis=1)

    json_data = json.dumps({
        "samples": [float(s) for s in downsampled_max_hold],
        "frequency_start": data.frequency_start,
        "frequency_span": data.frequency_span
    })

    return json_data




