from PIL import Image, ImageChops, ImageDraw
from random import randint
import numpy as np

class SpindaConfig:
    sprite_base = Image.open("res/spinda_base.png")
    sprite_mask = Image.open("res/spinda_mask.png")
    spot_masks = [
        np.array(Image.open("res/spots/spot_1.png")),
        np.array(Image.open("res/spots/spot_2.png")),
        np.array(Image.open("res/spots/spot_3.png")),
        np.array(Image.open("res/spots/spot_4.png"))
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

    def is_spot_n(self, pos, n):
        pos_adjusted = (
            pos[0] - self.spot_offsets[n][0] - self.spots[n][0],
            pos[1] - self.spot_offsets[n][1] - self.spots[n][1]
        )
        mask = self.spot_masks[n]

        # if the position lies outside the spot image: return false
        if pos_adjusted[0] < 0 or pos_adjusted[1] < 0 or pos_adjusted[0] >= len(mask[0]) or pos_adjusted[1] >= len(mask):
            return False
        
        # else: return true if the corresponding pixel is opaque
        mask_pixel = mask[pos_adjusted[1]][pos_adjusted[0]][3]
        if mask_pixel == 255:
            return True
        return False

    def is_spot(self, pos):
        if self.is_spot_n(pos, 0): return True
        if self.is_spot_n(pos, 1): return True
        if self.is_spot_n(pos, 2): return True
        if self.is_spot_n(pos, 3): return True
        return False

    def render_pattern(self, only_pattern = False, crop = False):
        size = self.sprite_base.size
        img = self.sprite_base.copy()

        mask_arr = np.asarray(self.sprite_mask)

        draw = ImageDraw.ImageDraw(img)

        for x in range(size[0]):
            for y in range(size[1]):
                # apply mask
                mask_pixel = tuple(mask_arr[y][x])

                if self.is_spot((x, y)) and mask_pixel[3] != 0:
                    if only_pattern:
                        draw.point((x, y), (255, 255, 255, 255))
                    else:
                        draw.point((x, y), mask_pixel)
                elif only_pattern:
                        draw.point((x, y), (0, 0, 0, 255))

        if crop: img = img.crop((17, 15, 52, 48))

        return img

    def get_difference(self, target):
        result = self.render_pattern(only_pattern=True, crop=True).convert("RGB")
        diff = ImageChops.difference(target, result)

        total_diff = 0
        for x in range(result.size[0]):
            for y in range(result.size[1]):
                pix = diff.getpixel((x, y))
                val = (pix[0] + pix[1] + pix[2])/3
                total_diff += val

        return total_diff

if __name__ == "__main__":
    spin = SpindaConfig.from_personality(0x7a397866)
    spin.render_pattern().show()
    #print(hex(spin.get_personality()))