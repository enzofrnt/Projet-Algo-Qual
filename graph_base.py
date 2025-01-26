import time
from collections import defaultdict
import geopy.distance as distance
from abc import ABC, abstractmethod
from path_finder import DijkstraPathFinder, AStarPathFinder


class BaseGraph(ABC):
    def __init__(self):
        self.nodes = {}
        self.edges = defaultdict(list)
        self.name_to_ids = defaultdict(list)
        self.pathfinders = {
            "dijkstra": DijkstraPathFinder(),
            "astar": AStarPathFinder()
        }
        self.current_pathfinder = "astar"

    @abstractmethod
    def load_from_csv(self, nodes_file, ways_file):
        """Méthode abstraite à implémenter par les classes filles"""
        pass

    def add_node(self, node_id, lat, lon, name):
        self.nodes[node_id] = (float(lat), float(lon), name)
        if name:
            self.name_to_ids[name].append(node_id)

    def add_edge(self, from_id, to_id, distance):
        self.edges[from_id].append((to_id, float(distance)))
        self.edges[to_id].append((from_id, float(distance)))

    def get_node_by_name(self, name):
        """Return all nodes matching the given name."""
        return [(node_id, self.nodes[node_id]) for node_id in self.name_to_ids[name]]

    def calculate_distance(self, from_node, to_node):
        """Calculate straight-line distance between two nodes using their coordinates."""
        from_lat, from_lon, _ = self.nodes[from_node]
        to_lat, to_lon, _ = self.nodes[to_node]
        return distance.distance((from_lat, from_lon), (to_lat, to_lon)).km
    
    def _reconstruct_path(self, came_from, start_id, end_id):
        """Reconstruit le chemin à partir du dictionnaire came_from."""
        path = []
        current = end_id
        
        while current is not None:
            path.append(current)
            current = came_from.get(current)
            
        path.reverse()
        return path if path and path[0] == start_id else None
    
    def find_path(self, from_id, to_id):
        start_time = time.time()
        pathfinder = self.pathfinders[self.current_pathfinder]
        path, total_distance = pathfinder.find_path(self, from_id, to_id)
        search_time = time.time() - start_time

        if not path:
            return None

        from_lat, from_lon, from_name = self.nodes[from_id]
        to_lat, to_lon, to_name = self.nodes[to_id]
        direct_distance = self.calculate_distance(from_id, to_id)

        result = {
            "from": {
                "id": from_id,
                "name": from_name,
                "coordinates": (from_lat, from_lon),
            },
            "to": {"id": to_id, "name": to_name, "coordinates": (to_lat, to_lon)},
            "path": path,
            "path_distance": total_distance,
            "direct_distance": direct_distance,
            "search_time": search_time,
            "algorithm": self.current_pathfinder
        }
        return result

    def format_path_info(self, path_info):
        """Formate les informations du chemin pour un affichage plus lisible."""
        if not path_info:
            return "Aucun chemin trouvé."
        
        if path_info['path_distance'] == float('inf'):
            return f"\nAucun chemin trouvé entre {path_info['from']['name']} et {path_info['to']['name']}"
        
        result = "\n" + "="*50 + "\n"
        result += f"Algorithme : {self.current_pathfinder.upper()}\n"
        result += f"Chemin de {path_info['from']['name']} à {path_info['to']['name']}\n"
        result += "-"*50 + "\n"
        result += f"Distance totale du trajet : {path_info['path_distance']:.2f} km\n"
        result += f"Distance à vol d'oiseau : {path_info['direct_distance']:.2f} km\n"
        result += f"Temps de recherche : {path_info['search_time'] * 1000:.2f} ms\n"
        
        return result

    def compare_algorithms(self, start_name, end_name):
        """Compare les résultats entre A* et Dijkstra"""
        results = {}
        node_id_start = self.find_node_id_by_name(start_name)
        node_id_end = self.find_node_id_by_name(end_name)

        if not node_id_start or not node_id_end:
            print(f"\nErreur: Point non trouvé: {start_name if not node_id_start else end_name}")
            return

        for algo_name in self.pathfinders:
            self.current_pathfinder = algo_name
            results[algo_name] = self.find_path(node_id_start, node_id_end)

        self._print_comparison_results(results)

    def find_node_id_by_name(self, name):
        if name in self.name_to_ids:
            return self.name_to_ids[name][0]
        return None

def find_destinations(graph, destinations):
    for destination in destinations:
        node_id_start = graph.find_node_id_by_name(depart)
        node_id_end = graph.find_node_id_by_name(destination)
        
        if node_id_start and node_id_end:
            path_info = graph.find_path(node_id_start, node_id_end)
            print(graph.format_path_info(path_info))
        else:
            print(f"\nErreur: Impossible de trouver {'le point de départ' if not node_id_start else 'la destination'}")
            
            
if __name__ == "__main__":
    start_time = time.time()
    
    # Initialisation du graph
    graph = BaseGraph()
    # Chargez vos gros fichiers CSV (plus efficace en multiprocess)
    # Ex. pour Serres-sur-arget :
    # graph.load_from_csv("data/serres-sur-arget/osm_nodes.csv",
    #                     "data/serres-sur-arget/osm_ways.csv")x

    # Ou pour l'Ariège :
    graph.load_from_csv("data/ariege/osm_nodes.csv", "data/ariege/osm_ways.csv")
    
    end_time = time.time()
    print(f"\nTemps total (main) de chargement et préparation : {end_time - start_time:.2f} secondes")

    # Points de test
    depart = "Saint-Pierre-de-Rivière"
    destinations = ["Saint-Pierre-de-Rivière", "Las Prados"]

    # Comparaison des algorithmes pour chaque destination
    for destination in destinations:
        graph.compare_algorithms(depart, destination)
    
    
    
    
    
    

