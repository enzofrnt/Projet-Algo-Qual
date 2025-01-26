import pandas as pd
import time
from graph_base import BaseGraph

class GraphPanda(BaseGraph):
    def load_from_csv(self, nodes_file, ways_file):
            """
            Charge les données CSV via pandas pour de meilleures performances
            """
            start_time = time.time()

            # 1) Lecture rapide via pandas
            df_nodes = pd.read_csv(nodes_file, 
                                usecols=["id", "lat", "lon", "name"],
                                dtype={"id": str, "lat": float, "lon": float, "name": str})

            df_ways = pd.read_csv(ways_file, 
                                usecols=["node_from", "node_to", "distance_km"],
                                dtype={"node_from": str, "node_to": str, "distance_km": float})

            # 2) Construction du graphe
            # Pass 1: Nœuds
            for row in df_nodes.itertuples(index=False):
                self.add_node(row.id, row.lat, row.lon, row.name)

            # Pass 2: Arêtes
            for row in df_ways.itertuples(index=False):
                self.add_edge(row.node_from, row.node_to, row.distance_km)

            end_time = time.time()
            print(f"Chargement terminé en {end_time - start_time:.2f} s.")