class Chromosome:
    def __init__(self, chromosome):
        self.chromosome = chromosome
        self.fitness = 0

    def set_fitness(self, fitness):
        self.fitness = fitness

    def add_fitness(self, new_fitness):
        self.fitness += new_fitness

    def reset_fitness(self):
        self.fitness = 0

    # Override __getitem__ to allow direct access to chromosome list
    def __getitem__(self, index):
        return self.chromosome[index]

    # Override __eq__
    def __eq__(self, other):
        return isinstance(other, Chromosome) and self.chromosome == other.chromosome

    def __hash__(self):
        return hash(tuple(self.chromosome))