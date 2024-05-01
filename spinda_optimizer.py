from PIL import Image
from spindafy import SpindaConfig as Spinda
from random import choice, random, randint
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from timeify import timeify
import copy

PREDEFINED = {
    "ALL_WHITE": 0x393d9888,
    "ALL_BLACK": 0xff200000
}

def create_offspring(parent1, parent2):
    MUTATION_PROB = 0.2
    
    offspring = Spinda()
    
    for n in range(4):
        # recombination
        offspring.spots[n] = choice((parent1, parent2)).spots[n]

        # very basic mutation!!
        if random() <= MUTATION_PROB:
            offspring.spots[n] = (randint(0, 15), randint(0, 15))

    return offspring

def generate_parents(pop_fitness):
    pop = len(pop_fitness)
    parent_1 = pop_fitness[int(random() ** 2 * pop)]
    parent_2 = parent_1
    while parent_2 == parent_1:
        parent_2 = pop_fitness[int(random() ** 2 * pop)]
    return (parent_1[0], parent_2[0])

# @timeify
def get_pop_fitness(spinda, target, spot_masks, sprite_mask):
    # deep copy the masks to make them thread safe
    spot_masks_local = copy.deepcopy(spot_masks)
    sprite_mask_local = copy.deepcopy(sprite_mask)
    return (spinda, spinda.get_difference(target, spot_masks_local, sprite_mask_local))

# @timeify
def evolve_step(target, population, elitism_count=2):
    num_workers = len(population)

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        spot_masks = Spinda.spot_masks
        sprite_mask = Spinda.sprite_mask
        # Load the masks so they can be deep copied later
        for img in spot_masks:
            img.load()
        sprite_mask.load()
        # Submitting jobs to the thread pool and collecting futures
        futures = [executor.submit(get_pop_fitness, pop, target, spot_masks, sprite_mask) for pop in population]
        # Retrieving results as they are completed
        pop_fitness = [future.result() for future in as_completed(futures)]

    
    # Sorting based on fitness
    pop_fitness = sorted(pop_fitness, key=lambda t: t[1])
    (best_spinda, best_fitness) = pop_fitness[0]
    pop = len(population)

    new_pop = [x[0] for x in pop_fitness[:elitism_count]]  # carry over the top elites

    for _ in range(pop - elitism_count):
        (parent_1, parent_2) = generate_parents(pop_fitness)
        new_pop.append(create_offspring(parent_1, parent_2))

    return (new_pop, best_fitness, best_spinda)

@timeify
def evolve(target, pop, n_generations, include = []):

    # check for predefined spinda patterns!
    black_target = [127, 127, 127, 255] if target.mode == "RBGA" else 127
    if np.all(np.greater_equal(target, 128)):
        best_spinda = Spinda.from_personality(PREDEFINED["ALL_WHITE"])
        print(f"Found predefined Spinda: 'ALL_WHITE': {hex(best_spinda.get_personality())}")
        return (best_spinda.get_difference(target, Spinda.spot_masks, Spinda.sprite_mask), best_spinda)
    if np.all(np.less_equal(target, black_target)):
        best_spinda = Spinda.from_personality(PREDEFINED["ALL_BLACK"])
        print(f"Found predefined Spinda: 'ALL_BLACK': {hex(best_spinda.get_personality())}")
        return (best_spinda.get_difference(target, Spinda.spot_masks, Spinda.sprite_mask), best_spinda)
        
    # create a population of spinda
    population = [Spinda.random() for _ in range(pop - len(include))]
    # insert prepopulation
    for spinda in include: population.append(spinda)

    best_fitness, best_spinda = (None, None)

    # run evolution
    for gen in range(n_generations):
        (population, best_fitness, best_spinda) = evolve_step(target, population)
        print(f"Generation #{gen} // best: {hex(best_spinda.get_personality())} ({best_fitness})")
    
    return (best_fitness, best_spinda)

def render_to_spinda(filename, pop, n_generations, include = []) -> Image:
    with Image.open(filename) as target:
        (_, best_spinda) = evolve(target.convert("RGB"), pop, n_generations)
        return (best_spinda.render_pattern(), best_spinda)

if __name__ == "__main__":
    (img, best) = render_to_spinda("res/test_large.png", 250, 25)
    img.resize((1000, 1000), Image.Resampling.NEAREST).show()