from glob import glob
from pathlib import Path
from argparse import ArgumentParser
from large_spinda import to_spindas
import json

GENERATIONS = 10
POPULATION = 100

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("input_directory")
    parser.add_argument("output_directory")

    args = parser.parse_args()

    # find all input images
    inputs = glob(args.input_directory + "/*")

    # create output directories if they don't exist
    Path(args.output_directory).mkdir(parents=True, exist_ok=True)
    Path(args.output_directory + "/pids").mkdir(parents=True, exist_ok=True)

    for n, filename in enumerate(inputs):
        print(f"STARTING FRAME #{n:0>4}! — ({n/len(inputs) * 100}%)")

        if len(glob(args.output_directory + f"/frame{n:0>4}_*")) > 0:
            print("frame already found! skipping.")
            continue

        (img, pids) = to_spindas(filename, POPULATION, GENERATIONS)

        output_filename = args.output_directory + f"/frame{n:0>4}.png"
        img.save(output_filename)

        # write PIDs to JSON files:
        with open(args.output_directory + f"/pids/frame{n:0>4}.json", "w") as f:
            json.dump(pids, f)