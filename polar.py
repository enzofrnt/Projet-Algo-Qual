import polars as pl
import heapq
import time
from collections import defaultdict
import geopy.distance as distance

class Graph:
    def __init__(self, resolver="dijkstra"):
        self.nodes = {}
        self.edges = defaultdict(list)
        self.name_to_ids = defaultdict(list)
        self.resolver = resolver

    def add_node(self, node_id, lat, lon, name):
        self.nodes[node_id] = (float(lat), float(lon), name)
        if name:
            self.name_to_ids[name].append(node_id)

    def add_edge(self, from_id, to_id, dist):
        distance_float = float(dist)
        self.edges[from_id].append((to_id, distance_float))
        self.edges[to_id].append((from_id, distance_float))

    def load_from_csv(self, nodes_file, ways_file):
        """
        Charge les données CSV via polars pour de meilleures performances
        """
        start_time = time.time()

        # 1) Lecture rapide via polars
        df_nodes = pl.read_csv(nodes_file, 
                             columns=["id", "lat", "lon", "name"],
                             schema_overrides={"id": pl.Utf8, 
                                    "lat": pl.Float64,
                                    "lon": pl.Float64,
                                    "name": pl.Utf8})

        df_ways = pl.read_csv(ways_file, 
                            columns=["node_from", "node_to", "distance_km"],
                            schema_overrides={"node_from": pl.Utf8,
                                   "node_to": pl.Utf8,
                                   "distance_km": pl.Float64})

        # 2) Construction du graphe
        # Pass 1: Nœuds
        for row in df_nodes.iter_rows(named=True):
            self.add_node(row["id"], row["lat"], row["lon"], row["name"])

        # Pass 2: Arêtes
        for row in df_ways.iter_rows(named=True):
            self.add_edge(row["node_from"], row["node_to"], row["distance_km"])

        end_time = time.time()
        print(f"Chargement terminé en {end_time - start_time:.2f} s.")

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
    
    def astar(self, start_id, end_id):
        """
        Algorithme de recherche de chemin A* :
        - g_score : coût réel pour atteindre chaque nœud depuis le start.
        - f_score : g_score + heuristique (distance à vol d'oiseau).
        - closed_set : ensemble des nœuds déjà explorés avec un coût minimal garanti.
        """
        if start_id not in self.nodes or end_id not in self.nodes:
            return None, float("inf")

        g_score = defaultdict(lambda: float('inf'))
        f_score = defaultdict(lambda: float('inf'))
        came_from = {}
        closed_set = set()

        g_score[start_id] = 0
        f_score[start_id] = self.calculate_distance(start_id, end_id)

        open_set = []
        heapq.heappush(open_set, (f_score[start_id], start_id))

        while open_set:
            current_f, current_node = heapq.heappop(open_set)

            if current_node == end_id:
                # On a atteint la destination
                return self._reconstruct_path(came_from, start_id, end_id), g_score[end_id]

            closed_set.add(current_node)

            if current_f > f_score[current_node]:
                # f_score obsolète
                continue

            for neighbor, weight in self.edges[current_node]:
                if neighbor in closed_set:
                    continue

                tentative_g_score = g_score[current_node] + weight
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current_node
                    g_score[neighbor] = tentative_g_score
                    # heuristique (distance droite)
                    h = self.calculate_distance(neighbor, end_id)
                    f_score[neighbor] = tentative_g_score + h
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None, float("inf")

    def dijkstra(self, start_id, end_id):
        if start_id not in self.nodes or end_id not in self.nodes:
            return None, float("inf")

        distances = {node: float("inf") for node in self.nodes}
        distances[start_id] = 0
        previous = {node: None for node in self.nodes}
        pq = [(0, start_id)]

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_node == end_id:
                break

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in self.edges[current_node]:
                new_dist = current_distance + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (new_dist, neighbor))

        path = []
        current = end_id
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()

        if distances[end_id] == float("inf"):
            return None, float("inf")
        return path, distances[end_id]
    
    def find_node_id_by_name(self, name):
        if name in self.name_to_ids:
            return self.name_to_ids[name][0]
        return None

    def find_path(self, from_id, to_id):
        """Find and format path information between two nodes."""
        start_time = time.time()
        
        if self.resolver == "dijkstra":
            path, total_distance = self.dijkstra(from_id, to_id)
        else:
            path, total_distance = self.astar(from_id, to_id)
            
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
            "to": {
                "id": to_id,
                "name": to_name,
                "coordinates": (to_lat, to_lon)
            },
            "path": path,
            "path_distance": total_distance,
            "direct_distance": direct_distance,
            "search_time": search_time,
            "algorithm": self.resolver
        }
        return result

    def format_path_info(self, path_info):
        """Formate les informations du chemin pour un affichage plus lisible."""
        if not path_info:
            return "Aucun chemin trouvé."
        if path_info['path_distance'] == float('inf'):
            return f"\nAucun chemin trouvé entre {path_info['from']['name']} et {path_info['to']['name']}"

        result = "\n" + "="*50 + "\n"
        result += f"Algorithme : {path_info['algorithm'].upper()}\n"
        result += f"Chemin de {path_info['from']['name']} à {path_info['to']['name']}\n"
        result += "-"*50 + "\n"
        result += f"Distance totale du trajet : {path_info['path_distance']:.2f} km\n"
        result += f"Distance à vol d'oiseau : {path_info['direct_distance']:.2f} km\n"
        result += f"Temps de recherche : {path_info['search_time'] * 1000:.2f} ms\n"
        return result

    def compare_algorithms(self, start_name, end_name):
        """Compare les résultats entre A* et Dijkstra pour un même trajet."""
        node_id_start = self.find_node_id_by_name(start_name)
        node_id_end = self.find_node_id_by_name(end_name)
        
        if not node_id_start or not node_id_end:
            print(f"\nErreur: Impossible de trouver "
                  f"{'le point de départ' if not node_id_start else 'la destination'} "
                  f"('{start_name if not node_id_start else end_name}')")
            return
            
        # Test avec Dijkstra
        self.resolver = "dijkstra"
        dijkstra_result = self.find_path(node_id_start, node_id_end)
        
        # Test avec A*
        self.resolver = "astar"
        astar_result = self.find_path(node_id_start, node_id_end)
        
        # Affichage des résultats
        print("\nCOMPARAISON DES ALGORITHMES")
        print("="*50)
        
        if dijkstra_result and astar_result:
            print(f"\nTrajet : {start_name} → {end_name}")
            print("\nDijkstra :")
            print(f"- Temps de recherche : {dijkstra_result['search_time'] * 1000:.2f} ms")
            print(f"- Distance : {dijkstra_result['path_distance']:.2f} km")
            print(f"- Nombre de nœuds : {len(dijkstra_result['path'])}")
            
            print("\nA* :")
            print(f"- Temps de recherche : {astar_result['search_time'] * 1000:.2f} ms")
            print(f"- Distance : {astar_result['path_distance']:.2f} km")
            print(f"- Nombre de nœuds : {len(astar_result['path'])}")
            
            # Comparaison des performances
            time_diff = 0
            if dijkstra_result['search_time'] != 0:
                time_diff = ((dijkstra_result['search_time']
                              - astar_result['search_time'])
                             / dijkstra_result['search_time']) * 100
            sign = "plus rapide" if time_diff > 0 else "plus lent"
            print(f"\nA* est {abs(time_diff):.1f}% {sign} que Dijkstra")

            # Vérification si les chemins sont identiques
            paths_identical = (dijkstra_result['path'] == astar_result['path'])
            print(f"Les chemins trouvés sont {'identiques' if paths_identical else 'différents'}")
        else:
            print(f"\nErreur: Impossible de trouver un chemin entre '{start_name}' et '{end_name}'")
            print("Détails :")
            print(f"- Point de départ trouvé: {start_name} (ID: {node_id_start})")
            print(f"- Destination trouvée: {end_name} (ID: {node_id_end})")
            print(f"- Résultat Dijkstra: {'Échec' if not dijkstra_result else 'Succès'}")
            print(f"- Résultat A*: {'Échec' if not astar_result else 'Succès'}")
            
            if node_id_start in self.edges and node_id_end in self.edges:
                print("Les deux points existent dans le graphe mais ne sont pas connectés.")
                print(f"Nombre de connexions pour {start_name}: {len(self.edges[node_id_start])}")
                print(f"Nombre de connexions pour {end_name}: {len(self.edges[node_id_end])}")
            else:
                print("Au moins un des points n'a pas de connexions dans le graphe.")


def find_destinations(graph, destinations, depart):
    """
    Lance la recherche de chemin pour plusieurs destinations.
    """
    for destination in destinations:
        node_id_start = graph.find_node_id_by_name(depart)
        node_id_end = graph.find_node_id_by_name(destination)
        
        if node_id_start and node_id_end:
            path_info = graph.find_path(node_id_start, node_id_end)
            print(graph.format_path_info(path_info))
        else:
            print(f"\nErreur: Impossible de trouver "
                  f"{'le point de départ' if not node_id_start else 'la destination'}")


if __name__ == "__main__":
    start_time = time.time()
    
    # Initialisation du graph
    graph = Graph(resolver="dijkstra")
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