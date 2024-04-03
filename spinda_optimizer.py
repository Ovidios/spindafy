from PIL import Image
from spindafy import SpindaConfig
from random import choice, random, randint
import multiprocessing, numpy as np
from itertools import repeat, starmap

PREDEFINED = {
    "ALL_WHITE": 0x393d9888,
    "ALL_BLACK": 0xff200000
}

try:
    cpus = multiprocessing.cpu_count()
except NotImplementedError:
    cpus = 2   # arbitrary default

def create_offspring(parent1, parent2):
    MUTATION_PROB = 0.2
    
    offspring = SpindaConfig()
    
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

def get_pop_fitness(spinda, target):
    return (spinda, spinda.get_difference(target))

def evolve_step(target, population):
    pool = multiprocessing.Pool(processes=cpus)
    pop_fitness = pool.starmap(get_pop_fitness, zip(population, repeat(target)))
    #pop_fitness = starmap(get_pop_fitness, zip(population, repeat(target)))
    pop_fitness = sorted(pop_fitness, key=lambda t: t[1])
    (best_spinda, best_fitness) = pop_fitness[0]
    pop = len(population)

    new_pop = []
    for _ in range(pop):
        (parent_1, parent_2) = generate_parents(pop_fitness)
        new_pop.append(create_offspring(parent_1, parent_2))
    return (new_pop, best_fitness, best_spinda)

def evolve(target, pop, n_generations, include = []):
    # check for predefined spinda patterns!
    black_target = [127, 127, 127, 255] if target.mode == "RBGA" else 127
    if np.all(np.greater_equal(target, 128)):
        best_spinda = SpindaConfig.from_personality(PREDEFINED["ALL_WHITE"])
        print(f"Found predefined Spinda: 'ALL_WHITE': {hex(best_spinda.get_personality())}")
        return (best_spinda.get_difference(target), best_spinda)
    if np.all(np.less_equal(target, black_target)):
        best_spinda = SpindaConfig.from_personality(PREDEFINED["ALL_BLACK"])
        print(f"Found predefined Spinda: 'ALL_BLACK': {hex(best_spinda.get_personality())}")
        return (best_spinda.get_difference(target), best_spinda)
        
    # create a population of spinda
    population = [SpindaConfig.random() for _ in range(pop - len(include))]
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
    (img, best) = render_to_spinda("badapple/frame6476.png", 250, 25)
    img.resize((1000, 1000), Image.Resampling.NEAREST).show()