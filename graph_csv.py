import csv
from graph_base import BaseGraph

class GraphCSV(BaseGraph):
    def load_from_csv(self, nodes_file, ways_file):
        with open(nodes_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.add_node(row["id"], row["lat"], row["lon"], row["name"])

        with open(ways_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.add_edge(row["node_from"], row["node_to"], row["distance_km"])