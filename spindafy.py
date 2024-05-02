from PIL import Image, ImageChops, ImageDraw
from random import randint
import numpy as np
from numba import cuda
import config

class SpindaConfig:
    sprite_base = Image.open("res/spinda_base.png")
    sprite_mask = Image.open("res/spinda_mask.png")
    spot_masks = [
        Image.open("res/spots/spot_1.png"),
        Image.open("res/spots/spot_2.png"),
        Image.open("res/spots/spot_3.png"),
        Image.open("res/spots/spot_4.png")
    ]
    spot_offsets = [
        (8, 6),
        (32, 7),
        (14, 24),
        (26, 25)
    ]
    def __init__(self):
        self.spots = [
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0)
        ]

    def __str__(self):
        return f"<SpindaConfig> {self.spots}"

    @staticmethod
    def from_personality(pers):
        self = SpindaConfig()
        self.spots[0] = (pers & 0x0000000f, (pers & 0x000000f0) >> 4)
        self.spots[1] = ((pers & 0x00000f00) >> 8, (pers & 0x0000f000) >> 12)
        self.spots[2] = ((pers & 0x000f0000) >> 16, (pers & 0x00f00000) >> 20)
        self.spots[3] = ((pers & 0x0f000000) >> 24, (pers & 0xf0000000) >> 28)
        return self

    @staticmethod
    def random():
        return SpindaConfig.from_personality(randint(0, 0x100000000))

    def get_personality(self):
        pers = 0x00000000
        for i, spot in enumerate(self.spots):
            pers = pers | (spot[0] << i*8) | (spot[1] << i*8+4)
        return pers

    def render_pattern(self, only_pattern = False, crop = False):
        # Prepare a result image with the same size as base and bg either black or transparent
        size = self.sprite_base.size
        img = Image.new('RGBA', size, (0, 0, 0, 255 if only_pattern else 0))

        # When wanting an actual spinda, start by pasting in the base sprite
        if not only_pattern:
            img.paste(self.sprite_base, (0, 0))

        for index in range(4):
            # Calculate the top-left coordinate for the spot image
            position = (self.spot_offsets[index][0] + self.spots[index][0],
                        self.spot_offsets[index][1] + self.spots[index][1])

            # Create a full-size image for the full spot at the desired position,
            #   as composite operation requires same-sized images
            spot_full = Image.new('RGBA', size, (0, 0, 0, 0))
            spot_full.paste(self.spot_masks[index], position, mask=self.spot_masks[index])

            # Create temporary mask by combining mask and spot mask
            temp_mask = Image.new('RGBA', size, (0, 0, 0, 0))
            temp_mask.paste(self.sprite_mask, (0, 0), mask=spot_full)

            if only_pattern:
                # Composite the white spot onto the masked area
                temp_mask = Image.composite(spot_full, temp_mask, temp_mask)

            # Composite the new mask with the current result
            img = Image.composite(temp_mask, img, temp_mask)

        if crop:
            img = img.crop((17, 15, 52, 48))

        return img

    def get_difference(self, target):
        # Validate the mode will match the type used in the next step
        if target.mode != "RGB":
            target = target.convert("RGB")
        # Compare the resulting images by the total average pixel difference
        result = self.render_pattern(only_pattern=True, crop=True).convert("RGB")
        diff = ImageChops.difference(target, result)
        total_diff = 0
        for n, (r, g, b) in diff.getcolors():  # gives a list of counter and RGB values in the image
            total_diff += n*((r+g+b)/3)
        return total_diff

def get_differences_gpu(spindas, tdata, length):
    # Compare the resulting images by the total average pixel difference
    difference_tuples = []
    for spinda in spindas:
        result = spinda.render_pattern(only_pattern=True, crop=True).convert("RGB")
        rdata = np.array(result.getdata())
        diffs = np.zeros(length, dtype=np.uint64)
        rdata = cuda.to_device(rdata)
        diffs = cuda.to_device(diffs)
        get_difference_direct[int(length / 1024) + 1, 1024](tdata, rdata, diffs)
        difference_tuples.append((spinda, sum_reduce(diffs)))
    return difference_tuples


@cuda.reduce
def sum_reduce(a, b):
    return a + b

@cuda.jit
def get_difference_direct(tdata, rdata, diffs):
    index = cuda.grid(1)
    tr, tg, tb = tdata[index]
    rr, rg, rb = rdata[index]
    diffs[index] = (abs(tr - rr) + abs(tg - rg) + abs(tb - rb)) / 3

if __name__ == "__main__":
    spin = SpindaConfig.from_personality(0x7a397866)
    spin.render_pattern().show()
    #print(hex(spin.get_personality()))