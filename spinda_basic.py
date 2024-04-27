from spindafy import SpindaConfig
import numpy as np
from PIL import Image

PREDEFINED = {
    "ALL_WHITE": 0xff200000,
    "ALL_BLACK": 0x393d9888
}

#ordering of pixels are from to left to bottom right
#px values are used when the pixel value is equal to or the closest to below it for the given key
PX_MAPS = (
    {0: 0xFE, 100:0xBF, 200: 0x00},
    {0: 0xF0, 30:0xA0, 15:0x0F, 200: 0x00},
    {0: 0x9C, 100:0x75, 150: 0x88, 200: 0xF0},
    {0: 0x87, 100:0x5F, 150: 0x7C, 200: 0xFF}
)
PX_MAPS_MAX_VAL = max([max(x.keys()) for x in PX_MAPS])
PX_MAPS_MIN_VAL_NOT_ZERO = max([max([y for y in x.keys() if y > 0]) for x in PX_MAPS])

def px_find_best_spotmask(pixel_index:int, pixel_value:int):
    best_spotmask_i = min(sorted(PX_MAPS[pixel_index].keys(), reverse = True), key=lambda x:max(x - pixel_value, 0))
    return PX_MAPS[pixel_index][best_spotmask_i] << (pixel_index * 8)

def px_array_find_best_pid(target:Image):
    black_target = (PX_MAPS_MIN_VAL_NOT_ZERO, PX_MAPS_MIN_VAL_NOT_ZERO, PX_MAPS_MIN_VAL_NOT_ZERO, PX_MAPS_MIN_VAL_NOT_ZERO) if target.mode == "RBGA" else PX_MAPS_MIN_VAL_NOT_ZERO
    white_target = (PX_MAPS_MAX_VAL, PX_MAPS_MAX_VAL, PX_MAPS_MAX_VAL, PX_MAPS_MAX_VAL) if target.mode == "RBGA" else PX_MAPS_MAX_VAL
    if np.all(np.greater_equal(target, white_target)):
        return PREDEFINED["ALL_WHITE"]
    elif np.all(np.less_equal(target, black_target)):
        return PREDEFINED["ALL_BLACK"]
    
    if target.size[1] != 2 or target.size[0] != 2:
        target = target.resize((2, 2), Image.Resampling.NEAREST)
    target = target.convert('L')
    target = list(target.getdata())
    
    ret = 0x00
    for px_pos, px_val in enumerate(target):
        ret |= px_find_best_spotmask(px_pos, px_val)
    return ret

def px_array_find_best_spinda(target:Image):
    return SpindaConfig.from_personality(px_array_find_best_pid(target))

if __name__ == "__main__":
    with Image.open("res/test_large.png") as target:
        spin = px_array_find_best_spinda(target)
        print(hex(spin.get_personality()))
        spin.render_pattern().show()