from PIL import Image, ImageChops
from random import randint
from timeify import timeify
import numpy as np

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

    # @timeify
    def render_pattern(self, spot_masks=None, sprite_mask=None, only_pattern = False, crop = False):
        # Prepare a result image with the same size as base and bg either black or transparent
        size = self.sprite_base.size
        img = Image.new('RGBA', size, (0, 0, 0, 255 if only_pattern else 0))
        if spot_masks is None:
            spot_masks = self.spot_masks
        if sprite_mask is None:
            sprite_mask = self.sprite_mask
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
            spot_full.paste(spot_masks[index], position, mask=spot_masks[index])

            # Create temporary mask by combining mask and spot mask
            temp_mask = Image.new('RGBA', size, (0, 0, 0, 0))
            temp_mask.paste(sprite_mask, (0, 0), mask=spot_full)

            if only_pattern:
                # Composite the white spot onto the masked area
                temp_mask = Image.composite(spot_full, temp_mask, temp_mask)

            # Composite the new mask with the current result
            img = Image.composite(temp_mask, img, temp_mask)

        if crop:
            img = img.crop((17, 15, 52, 48))

        return img    

    def get_difference(self, target, spot_masks, sprite_mask):
        # if target.mode != "L":
        #     target = target.convert("L")
        result = self.render_pattern(spot_masks, sprite_mask, only_pattern=True, crop=True).convert("L")
        target_np = np.array(target)
        result_np = np.array(result)

        # Compute absolute difference
        diff = np.abs(target_np - result_np)
        total_diff = np.sum(diff) / diff.size  # Normalize by the number of elements

        return total_diff

if __name__ == "__main__":
    spin = SpindaConfig.from_personality(0x7a397866)
    spin.render_pattern().show()
    #print(hex(spin.get_personality()))