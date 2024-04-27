from spinda_basic import px_array_find_best_spinda

from PIL import Image
import PIL.ImageOps

from spindafy import SpindaConfig

# this is only a slightly marginally better way of doing this!
def to_spindas(filename, invert = False, *, image_in_autocrop:bool = True, image_mode_override = None, image_in_scale = None, pixels_per_spinda = (25, 20), pixel_region_overlap = (10, 10), spinda_overlap = (0, 0),face_only:bool = False, log:bool = False):
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

        num_x = int((target.size[0])/pixels_per_spinda[0])
        num_y = int((target.size[1])/pixels_per_spinda[1])

        if log:
            print(f"Spinda count: {num_x} * {num_y}")

        #this can be a rough calculation to approximate the max possible size, as we can crop it later to the proper size
        img_max_size = ((num_x+2) * pixels_per_spinda[0], (num_y+2) * pixels_per_spinda[1])
        
        if log:
            print(f"Output size max: {img_max_size}")
        
        img = Image.new("RGBA", img_max_size)
        
        pids = []

        for y in range(num_y):
            pids += [[]]
            for x in range(num_x):
                if log:
                    print(f"Subimage {x+1}|{y+1}")
                
                px_region = (
                    max((x*pixels_per_spinda[0]) - int(pixel_region_overlap[0]/2), 0),
                    max((y*pixels_per_spinda[1]) - int(pixel_region_overlap[1]/2), 0),
                    min(((x+1)*pixels_per_spinda[0]) + int(pixel_region_overlap[0]/2), img_max_size[0]),
                    min(((y+1)*pixels_per_spinda[1]) + int(pixel_region_overlap[1]/2), img_max_size[1])
                )
                sub_target = target.crop(px_region)
                best_spinda = px_array_find_best_spinda(sub_target)
                spinmage = best_spinda.render_pattern(crop = face_only)
                spinmage = spinmage.crop(spinmage.getbbox())
                spin_size = (int(pixels_per_spinda[0] + (spinda_overlap[0]/2)), int(pixels_per_spinda[1] + (spinda_overlap[1]/2)))
                spin_place = (int(pixels_per_spinda[0] - (spinda_overlap[0]/2)), int(pixels_per_spinda[1] - (spinda_overlap[1]/2)))
                spinmage = spinmage.resize(spin_size)
                img.paste(
                    spinmage,
                    (spin_place[0] * x, spin_place[1] * y),
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
    
    (img, pids) = to_spindas("res/bestboy.png", image_mode_override ="L", spinda_overlap = (10, 10), face_only = head_only, log = debug)
    if debug:
        img.resize((img.size[0]*10, img.size[1]*10), Image.Resampling.NEAREST).show()
    img.save("basic/test_res.png")
    with open("basic/test.json", "w") as f:
        json.dump(pids, f)