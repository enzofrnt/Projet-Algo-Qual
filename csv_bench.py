import time
import matplotlib.pyplot as plt
from base import Graph as BaseGraph
from panda import Graph as PandasGraph
from polar import Graph as PolarGraph

def benchmark_implementation(graph_class, nodes_file, ways_file, name):
    start_time = time.time()
    graph = graph_class()
    graph.load_from_csv(nodes_file, ways_file)
    end_time = time.time()
    return end_time - start_time

def run_benchmarks():
    implementations = [
        (BaseGraph, "CSV (base)"),
        (PandasGraph, "Pandas"),
        (PolarGraph, "Polars"),
    ]
    
    datasets = [
        ("Serres", "data/serres-sur-arget/osm_nodes.csv", "data/serres-sur-arget/osm_ways.csv"),
        ("Ariège", "data/ariege/osm_nodes.csv", "data/ariege/osm_ways.csv")
    ]
    
    results = {}
    
    for dataset_name, nodes_file, ways_file in datasets:
        results[dataset_name] = []
        print(f"\nBenchmark pour {dataset_name}:")
        print("-" * 50)
        
        for graph_class, impl_name in implementations:
            time_taken = benchmark_implementation(graph_class, nodes_file, ways_file, impl_name)
            results[dataset_name].append((impl_name, time_taken))
            print(f"{impl_name}: {time_taken:.2f} secondes")

    return results

def plot_results(results):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    for i, (dataset, measurements) in enumerate(results.items()):
        names = [m[0] for m in measurements]
        times = [m[1] for m in measurements]
        
        ax = ax1 if i == 0 else ax2
        bars = ax.bar(names, times)
        ax.set_title(f"Temps de chargement - {dataset}")
        ax.set_ylabel("Temps (secondes)")
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}s',
                   ha='center', va='bottom')
        
        # Calculer les pourcentages d'amélioration
        csv_time = times[0]  # CSV (base)
        pandas_time = times[1]  # Pandas
        polars_time = times[2]  # Polars
        
        # Calculer les améliorations
        csv_pandas_improvement = ((csv_time - pandas_time) / csv_time) * 100
        pandas_polars_improvement = ((pandas_time - polars_time) / pandas_time) * 100
        csv_polars_improvement = ((csv_time - polars_time) / csv_time) * 100
        
        # Ajouter un texte en bas du graphique avec les améliorations
        improvements_text = (
            f"CSV → Pandas: {csv_pandas_improvement:.1f}% plus rapide\n"
            f"Pandas → Polars: {pandas_polars_improvement:.1f}% plus rapide\n"
            f"CSV → Polars: {csv_polars_improvement:.1f}% plus rapide"
        )
        
        # Placer le texte sous le graphique
        ax.text(0.5, -0.3, improvements_text,
                ha='center', va='center',
                transform=ax.transAxes,
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
        
    # Ajuster les marges pour accommoder le texte
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.25)  # Augmenter l'espace en bas
    plt.savefig('./img/benchmark_results.png')
    plt.close()

if __name__ == "__main__":
    results = run_benchmarks()
    plot_results(results)