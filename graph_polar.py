import polars as pl
import time
from graph_base import BaseGraph

class GraphPolar(BaseGraph):
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