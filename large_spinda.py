from PIL import Image
from spinda_optimizer import evolve
import json, PIL.ImageOps

# this is definitely not the best way of doing this!
def to_spindas(filename, pop, n_generations, invert = False):
    with Image.open(filename) as target:
        target = target.convert("RGB")
        if invert: target = PIL.ImageOps.invert(target)

        num_x = int((target.size[0]+10)/25)
        num_y = int((target.size[1]+13)/20)

        print(f"Size: {num_x} * {num_y}")

        img = Image.new("RGBA", (39 + num_x * 25, 44 + num_y * 20))
        pids = []

        for y in range(num_y):
            pids += [[]]
            for x in range(num_x):
                print(f"Subimage {x}|{y}")
                sub_target = target.crop((
                    x*25, y*20,
                    x*25+35,
                    y*20+33
                ))
                (_, best_spinda) = evolve(sub_target, pop, n_generations)
                spinmage = best_spinda.render_pattern()
                img.paste(
                    spinmage,
                    (x * 25, y * 20),
                    spinmage
                )
                pids[y] += [best_spinda.get_personality()]

        return (img, pids)
    
if __name__ == "__main__":
    (img, pids) = to_spindas("doom/test.png", 100, 10)
    img.resize((img.size[0]*10, img.size[1]*10), Image.Resampling.NEAREST).show()
    img.save("doom/test_res.png")
    with open("doom/test.json", "w") as f:
        json.dump(pids, f)