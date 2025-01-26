import time
import matplotlib.pyplot as plt
from graph_polar import GraphPolar

def benchmark_search(graph, start_name, end_name, algorithm):
    """Benchmark un algorithme spécifique"""
    graph.current_pathfinder = algorithm
    start_time = time.time()
    result = graph.find_path(
        graph.find_node_id_by_name(start_name),
        graph.find_node_id_by_name(end_name)
    )
    search_time = time.time() - start_time
    return search_time if result else float('inf')

def run_benchmarks():
    algorithms = [
        ("dijkstra", "Dijkstra"),
        ("astar", "A*")
    ]
    
    datasets = [
        ("Serres", "data/serres-sur-arget/osm_nodes.csv", "data/serres-sur-arget/osm_ways.csv"),
        ("Ariège", "data/ariege/osm_nodes.csv", "data/ariege/osm_ways.csv")
    ]
    
    paths = [
        ("Serres", "Saint-Pierre-de-Rivière", "Saint-Pierre-de-Rivière"),
        ("Ariège", "Saint-Pierre-de-Rivière", "Saint-Pierre-de-Rivière"),
        ("Serres", "Saint-Pierre-de-Rivière", "Las Prados"),
        ("Ariège", "Saint-Pierre-de-Rivière", "Las Prados"),
        ("Serres", "Saint-Pierre-de-Rivière", "Cabane Coumauzil - barguillere")
    ]
    
    results = {}
    graph = GraphPolar()
    
    for dataset_name, nodes_file, ways_file in datasets:
        graph.load_from_csv(nodes_file, ways_file)
        
        for data, start, end in paths:
            if dataset_name != data:
                continue
            
            dataset_label = f"{dataset_name} - {start} -> {end}"
            print(f"\nBenchmark pour {dataset_label}:")
            print("-" * 50)
            
            path_results = []
            for algo_id, algo_name in algorithms:
                time_taken = benchmark_search(graph, start, end, algo_id)
                path_results.append((algo_name, time_taken))
                print(f"{algo_name}: {time_taken * 1000:.2f} ms")
            
            results[dataset_label] = path_results
    
    return results

def plot_results(results):
    for dataset_label, measurements in results.items():
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_title(f"Temps de recherche - {dataset_label}")
        ax.set_ylabel("Temps (millisecondes)")
        
        names = [m[0] for m in measurements]
        times = [m[1] * 1000 for m in measurements]
        
        bars = ax.bar(names, times, width=0.8)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}ms',
                    ha='center', va='bottom')
        
        improvement = ((times[0] - times[1]) / times[0]) * 100
        ax.text(0.5, max(times) * 1.1,
                f"A* est {abs(improvement):.1f}%\n{'plus rapide' if improvement > 0 else 'plus lent'}",
                ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(f'./img/search_benchmark_{dataset_label.replace(" ", "_").replace("->", "to")}.png', bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    results = run_benchmarks()
    plot_results(results)
