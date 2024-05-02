from PIL import Image, ImageOps
from spinda_optimizer import evolve
import json
from timeify import timeify
import multiprocessing
from image_processing import process_image

try:
    cpus = multiprocessing.cpu_count()
except NotImplementedError:
    cpus = 2   # arbitrary default

def evolve_subimage(sub_target, pop, n_generations):
    (_, best_spinda) = evolve(sub_target, pop, n_generations)
    spinmage = best_spinda.render_pattern()
    personality = best_spinda.get_personality()
    return spinmage, personality

@timeify
def to_spindas(filename, pop, n_generations, invert=False):
    with Image.open(filename) as original_target:
        target = process_image(original_target)
        if invert:
            target = ImageOps.invert(target)
        # target.show()

        num_x = int((target.size[0] + 10) / 25)
        num_y = int((target.size[1] + 13) / 20)

        print(f"Size: {num_x} * {num_y}")

        img = Image.new("RGBA", (39 + num_x * 25, 44 + num_y * 20))
        results = []

        with multiprocessing.Pool(cpus) as pool:
            tasks = []
            for y in range(num_y):
                for x in range(num_x):
                    print(f"Subimage {x+1}|{y+1}")
                    sub_target = target.crop((
                        x * 25, y * 20,
                        x * 25 + 35,
                        y * 20 + 33
                    ))

                    # Launch a task for each subimage
                    task = pool.apply_async(evolve_subimage, (sub_target, pop, n_generations))
                    tasks.append((task, x, y))

            # Collect results
            for task, x, y in tasks:
                spinmage, personality = task.get()
                img.paste(spinmage, (x * 25, y * 20), spinmage)
                results.append((x, y, personality))

    return img, results
    
if __name__ == "__main__":
    (img, pids) = to_spindas("res/test_large.png", 100, 10, True)
    img.resize((img.size[0]*10, img.size[1]*10), Image.Resampling.NEAREST).show()
    img.save("res/test_result.png")
    with open("res/test.json", "w") as f:
        json.dump(pids, f)