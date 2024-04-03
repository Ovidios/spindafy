from glob import glob
from pathlib import Path
from argparse import ArgumentParser
from spinda_optimizer import evolve
from PIL import Image

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("input_directory")
    parser.add_argument("output_directory")

    args = parser.parse_args()

    # find all input images
    inputs = glob(args.input_directory + "/*")

    # create output directory if it doesn't exist
    Path(args.output_directory).mkdir(parents=True, exist_ok=True)

    for n, filename in enumerate(inputs):
        print(f"STARTING FRAME #{n:0>4}! — ({n/len(inputs) * 100}%)")

        if len(glob(args.output_directory + f"/frame{n:0>4}_*")) > 0:
            print("frame already found! skipping.")
            continue

        with Image.open(filename) as input_image:
            target = input_image.convert("RGB")

            (fitness, spinda) = evolve(target, 250, 25)
            spinmage = spinda.render_pattern()

            output_filename = args.output_directory + f"/frame{n:0>4}_{hex(spinda.get_personality())}.png"
            spinmage.save(output_filename)