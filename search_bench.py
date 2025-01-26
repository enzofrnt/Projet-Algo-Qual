import time
import pandas as pd
import matplotlib.pyplot as plt
from polar import Graph as AstarGraph

def benchmark_search(graph_class, nodes_file, ways_file, start_node, end_node):# Création et chargement du graphe
    graph = graph_class()
    start_time = time.time()
    graph.load_data(nodes_file, ways_file)
    load_time = time.time() - start_time
    
    # Recherche du chemin
    start_time = time.time()
    graph.find_path(start_node, end_node)
    search_time = time.time() - start_time
    
    return load_time, search_time

def run_search_benchmarks():
    # Fichiers de test de différentes tailles
    datasets = [
        ("small_nodes.csv", "small_ways.csv", "1", "100"),
        ("medium_nodes.csv", "medium_ways.csv", "1", "1000"), 
        ("large_nodes.csv", "large_ways.csv", "1", "10000")
    ]
    
    results = {
        "Base Dijkstra": [],
        "Pandas Dijkstra": [],
        "A*": []
    }
    
    for nodes_file, ways_file, start, end in datasets:
        # Test pour chaque implémentation
        for name, graph_class in [
            ("Base Dijkstra", BaseGraph),
            ("Pandas Dijkstra", PandasGraph),
            ("A*", AstarGraph)
        ]:
            load_time, search_time = benchmark_search(
                graph_class, 
                f"data/{nodes_file}", 
                f"data/{ways_file}",
                start,
                end
            )
            results[name].append(search_time)
            
    # Création du graphique
    datasets_names = ["Petit", "Moyen", "Grand"]
    x = range(len(datasets_names))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.bar([i - width for i in x], results["Base Dijkstra"], width, label="Dijkstra Base")
    ax.bar(x, results["Pandas Dijkstra"], width, label="Dijkstra Pandas")
    ax.bar([i + width for i in x], results["A*"], width, label="A*")
    
    ax.set_ylabel("Temps (secondes)")
    ax.set_title("Comparaison des temps de recherche")
    ax.set_xticks(x)
    ax.set_xticklabels(datasets_names)
    ax.legend()
    
    plt.savefig("img/search_benchmark.png")
    plt.close()

if __name__ == "__main__":
    run_search_benchmarks()
