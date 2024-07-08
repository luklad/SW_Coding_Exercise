from rtsa_decoder.DSPStreamFileChunkSamples import DSPStreamFileChunkSamples
from rtsa_decoder.chunk_id_map import get_chunk_object
from rtsa_decoder.rtsa_decoder import get_samples_from_file
from rtsa_decoder.rtsa_processing import get_heatmap_png, get_max_hold_json


def print_file_chunks(file_object):
    chunk_object = None
    while True:
        if chunk_object is None:
            chunk_object = get_chunk_object(file_object, 0, None)
        else:
            chunk_object = chunk_object.get_next_chunk()

        if chunk_object is None:
            break
        if not isinstance(chunk_object, DSPStreamFileChunkSamples):
            print()
            print(chunk_object.get_chunk_header_data())
            print(chunk_object.get_header_data())
        else:
            print("SAMP")


if __name__ == "__main__":
    with open("DOR_KU#1_1400932156.rtsa", "rb") as file_object:
        print_file_chunks(file_object)
        samples = get_samples_from_file(file_object)

    print(samples)
    heatmap_bytes = get_heatmap_png(samples)

    with open("samples.png", "wb") as heatmap_file:
        heatmap_file.write(heatmap_bytes)

    max_hold_json = get_max_hold_json(samples)

    with open("max_hold.json", "w") as max_hold_file:
        max_hold_file.write(max_hold_json)
