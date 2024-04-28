from math import ceil, floor
from spinda_basic import px_array_find_best_spinda
from spindafy import SpindaConfig

from PIL import Image
import PIL.ImageOps

def get_spinda_count(in_img_size, pixels_per_spinda):
    x = ceil(in_img_size[0] / pixels_per_spinda[0])
    y = ceil(in_img_size[1] / pixels_per_spinda[1])
    return (x,y)

def get_spinda_pixel_region(spinda_xy, in_img_size, pixels_per_spinda, pixel_region_overlap):
    x1 = max((spinda_xy[0] * pixels_per_spinda[0]) - pixel_region_overlap[0], 0)
    y1 = max((spinda_xy[1] * pixels_per_spinda[1]) - pixel_region_overlap[1], 0)
    x2 = min(((spinda_xy[0]+1) * pixels_per_spinda[0]) + pixel_region_overlap[0], in_img_size[0])
    y2 = min(((spinda_xy[1]+1) * pixels_per_spinda[1]) + pixel_region_overlap[1], in_img_size[1])
    return (x1,y1,x2,y2)

def get_spinda_pos(spinda_xy, out_img_size, spinda_size, spinda_overlap):
    x = (spinda_xy[0] * spinda_size[0])# - floor(spinda_overlap[0]/2)
    y = (spinda_xy[1] * spinda_size[1])# - floor(spinda_overlap[1]/2)
    # x = max(min(out_img_size[0], x), 0)
    # y = max(min(out_img_size[1], y), 0)
    print((x,y))
    return (x,y)

def get_out_img_size(spinda_count, spinda_size, spinda_overlap):
    x = ceil((max(spinda_count[0] - spinda_overlap[0], 0) + 1) * spinda_size[0])
    y = ceil((max(spinda_count[1] - spinda_overlap[1], 0) + 1) * spinda_size[1])
    return (x,y)

# this is only a slightly marginally better way of doing this!
def to_spindas(filename, invert = False, *, image_in_autocrop:bool = True, image_mode_override = None, image_in_scale = None, pixels_per_spinda = (25, 20), pixel_region_overlap = (5, 5), spinda_overlap = (0, 0),face_only:bool = False, log:bool = False):
    if pixels_per_spinda is None:
        pixels_per_spinda = (4,4)
    
    
    with Image.open(filename) as target:
        if image_mode_override is not None:
            target = target.convert(image_mode_override)
        if image_in_autocrop:
            target = target.crop(target.getbbox())
        if image_in_scale is not None:
            target = target.resize(image_in_scale, Image.Resampling.NEAREST)
        if invert:
            target = PIL.ImageOps.invert(target)
        
        if log:
            target.show()

        num_x, num_y = get_spinda_count(target.size, pixels_per_spinda)
        spinda_size = SpindaConfig.base_sprite_active_size(head_only)

        if log:
            print(f"Spinda count: {num_x} * {num_y}")

        #this can be a rough calculation to approximate the max possible size, as we can crop it later to the proper size
        img_max_size = get_out_img_size((num_x, num_y), spinda_size, spinda_overlap)
        
        if log:
            print(f"Output size max: {img_max_size}")
        
        img = Image.new("RGBA", img_max_size)
        
        pids = []

        for y in range(num_y):
            pids += [[]]
            for x in range(num_x):
                if log:
                    print(f"Subimage {x+1}|{y+1}")
                
                px_region = get_spinda_pixel_region((x,y), target.size, pixels_per_spinda, pixel_region_overlap)
                spin_place = get_spinda_pos((x,y), img_max_size, spinda_size, spinda_overlap)
                
                sub_target = target.crop(px_region)
                best_spinda = px_array_find_best_spinda(sub_target)
                spinmage = best_spinda.render_pattern(crop = face_only)
                
                #autocrop
                spinmage = spinmage.crop(spinmage.getbbox())
                
                img.paste(
                    spinmage,
                    spin_place,
                    spinmage
                )
                pids[y] += [best_spinda.get_personality()]

        img = img.crop(img.getbbox())
        return (img, pids)

if __name__ == "__main__":
    import json
    
    debug = True
    head_only = True
    #px_per = int(SpindaConfig.base_sprite_active_size(head_only)[0]/2), int(SpindaConfig.base_sprite_active_size(head_only)[1]/2)
    
    (img, pids) = to_spindas("res/bestboy.png", image_mode_override ="L", spinda_overlap = (-1, -1), image_in_scale = (100, 100), pixels_per_spinda = (4, 4), pixel_region_overlap=(3,3),face_only = head_only, log = debug)
    if debug:
        img.show()
    img.save("basic/test_res.png")
    with open("basic/test.json", "w") as f:
        json.dump(pids, f)