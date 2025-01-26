from abc import ABC, abstractmethod
import heapq
from collections import defaultdict

class PathFinder(ABC):
    @abstractmethod
    def find_path(self, graph, start_id, end_id):
        pass

class DijkstraPathFinder(PathFinder):
    def find_path(self, graph, start_id, end_id):
        if start_id not in graph.nodes or end_id not in graph.nodes:
            return None, float("inf")

        distances = {node: float("inf") for node in graph.nodes}
        distances[start_id] = 0
        previous = {node: None for node in graph.nodes}
        pq = [(0, start_id)]

        while pq:
            current_distance, current_node = heapq.heappop(pq)
            if current_node == end_id:
                break
            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in graph.edges[current_node]:
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))

        path = graph._reconstruct_path(previous, start_id, end_id)
        return path, distances[end_id]

class AStarPathFinder(PathFinder):
    def find_path(self, graph, start_id, end_id):
        if start_id not in graph.nodes or end_id not in graph.nodes:
            return None, float("inf")

        g_score = defaultdict(lambda: float('inf'))
        f_score = defaultdict(lambda: float('inf'))
        came_from = {}
        closed_set = set()

        g_score[start_id] = 0
        f_score[start_id] = graph.calculate_distance(start_id, end_id)
        open_set = [(f_score[start_id], start_id)]

        while open_set:
            current_f, current_node = heapq.heappop(open_set)
            if current_node == end_id:
                return graph._reconstruct_path(came_from, start_id, end_id), g_score[end_id]

            closed_set.add(current_node)
            if current_f > f_score[current_node]:
                continue

            for neighbor, weight in graph.edges[current_node]:
                if neighbor in closed_set:
                    continue

                tentative_g_score = g_score[current_node] + weight
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current_node
                    g_score[neighbor] = tentative_g_score
                    h = graph.calculate_distance(neighbor, end_id)
                    f_score[neighbor] = tentative_g_score + h
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None, float("inf") 