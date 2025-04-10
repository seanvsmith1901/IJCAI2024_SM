import csv
import statistics
import os
from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt


class Logger:
    def __init__(self):
        self.fitness_history = []
        self.diversity_history = []
        self.pca_snapshots = []
        self.cooperation_scores = []

    def log_generation(self, population, cooperation_score):
        fitnesses = [c.fitness for c in population]
        avg_fitness = statistics.mean(fitnesses)
        max_fitness = max(fitnesses)
        diversity = compute_diversity(population)

        self.fitness_history.append((avg_fitness, max_fitness, cooperation_score))
        self.diversity_history.append(diversity)

        gene_matrix = np.array([chrom.chromosome for chrom in population])
        pca = PCA(n_components=2)
        projected = pca.fit_transform(gene_matrix)
        self.pca_snapshots.append(projected)


    def save_logs(self, folder="logs"):
        print("Saving it all to a CSV...")
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "fitness.csv"), "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Generation", "Average", "Max", "Coop"])
            for i, (avg, max_) in enumerate(self.fitness_history):
                writer.writerow([i, avg, max_])
        with open(os.path.join(folder, "diversity.csv"), "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Generation", "Diversity"])
            for i, diversity in enumerate(self.diversity_history):
                writer.writerow([i, diversity])

    def plot_pca_snapshots(self, folder="logs"):
        os.makedirs(folder, exist_ok=True)
        for i, projection in enumerate(self.pca_snapshots):
            plt.figure(figsize=(6, 6))
            plt.scatter(projection[:, 0], projection[:, 1], alpha=0.6)
            plt.title(f"Population PCA (Gen {i})")
            plt.xlabel("PC1")
            plt.ylabel("PC2")
            plt.grid(True)
            plt.savefig(os.path.join(folder, f"pca_gen_{i}.png"))
            plt.close()

def compute_diversity(population):
    gene_matrix = np.array([chrom.chromosome for chrom in population])
    diversity = np.std(gene_matrix, axis=0).mean()
    return diversity