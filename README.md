# Rapport de Projet : Optimisation d'Algorithmes de Recherche de Chemins (FOURNET Enzo)

## Description du Projet

Le projet consiste à implémenter et optimiser des algorithmes de recherche de chemins sur des données OpenStreetMap.
L'objectif principal que j'ai choisi est de comparer les performances de deux approches :

- L'algorithme de Dijkstra
- L'algorithme A*

Les données sont fournies sous forme de fichiers CSV contenant :

- Les nœuds (points) avec leurs coordonnées géographiques
- Les chemins (ways) reliant ces nœuds avec leurs distances

*A noté que les données présente toujouts des anomalies, comme des points qui ne sont pas reliés à un chemin, ou des chemins qui ne sont pas reliés à un point. Ou même des points qui apparaissent plusieurs fois dans le fichier.*

## Problèmes Identifiés

### Temps de chargement des données

Il ne s'agit du problèmatique concernant les algorithmes eux même mais il semble tout de même nécessaire de rechercher à optimiser ce processus car il reste trés couteux et fais partie des processus dont nous avons besoin pour trouver un chemin.

L'implémentatin de base que j'avais mis en oeuvre que l'on retrouve dans le fichier `base.py` utilise la librairie `csv` qui semble être une des plus lente pour lire nos fichiers CSV.

```python
with open(nodes_file, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        self.add_node(row["id"], row["lat"], row["lon"], row["name"])

with open(ways_file, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        self.add_edge(row["node_from"], row["node_to"], row["distance_km"])
```

J'ai donc effectué des recherche et constater que `Pandas` était une librairie plus performante pour lire nos fichiers CSV. J'ai donc implémenté une version utilisant `Pandas` dans le fichier `pandas.py`:

```python
df_nodes = pd.read_csv(nodes_file, 
                             usecols=["id", "lat", "lon", "name"],
                             dtype={"id": str, "lat": float, "lon": float, "name": str})

df_ways = pd.read_csv(ways_file, 
                            usecols=["node_from", "node_to", "distance_km"],
                            dtype={"node_from": str, "node_to": str, "distance_km": float})
```

Le temps d'éxécution est bien meilleur mais il me semble toujours possible de l'optimiser.
Après d'autre recherche, j'ai découvert que `Polars` était une librairie encore plus performante pour lire nos fichiers CSV. Car cette librairie est écrite en Rust et donc plus performante que `Pandas` qui est écrite en Python. On retrouve cette version dans le fichier `polar.py`.

```python
df_nodes = pl.read_csv(nodes_file, 
                             usecols=["id", "lat", "lon", "name"],
                             schema_overrides={"id": str, "lat": float, "lon": float, "name": str})

df_ways = pl.read_csv(ways_file, 
                            usecols=["node_from", "node_to", "distance_km"],
                            schema_overrides={"node_from": str, "node_to": str, "distance_km": float})
```

En effectuant un benchmark de ces différente version voici les réusltat obrtenu :

![benchmark](./img/benchmark_results.png)

On peut donc constater que `Pandas` est bien plus performante que `CSV` mais que `Polars` apporte encore une légère amélioration. Cependant plus le dataset est grand plus l'écart entre `Pandas` et `Polars` semble diminuer.
Nous utilisertont donc pour la suite du projet `Polars` pour la lecture des fichiers CSV qui est dans notre cas le plus performant.

Le fichier python `csv_bench.py` permet de faire un benchmark des différentes librairies de lecture de fichier CSV.

### Algorithme de recherche

L'algorithme de recherche que j'ai implémenté est un algorithme de recherche de chemin qui utilise l'algorithme de Dijkstra. Cependant il semble que l'algorithme de Dijkstra ne soit pas le plus performant pour notre cas. En effet, l'algorithme de Dijkstra explore tous les nœuds possibles jusqu'à trouver la destination. Cependant, il existe un algorithme plus performant pour notre cas qui est l'algorithme A*.

#### Complexité de Calcul

- Dijkstra explore tous les nœuds possibles jusqu'à trouver la destination
- Calculs redondants de distances à vol d'oiseau
- Chargement initial des données coûteux pour de grands ensembles

#### Structure de Données

- Utilisation de dictionnaires Python pour stocker les nœuds et les arêtes
- Gestion de la mémoire pour les grands ensembles de données
- Conversion répétée des types de données (str/float)

#### Optimisations Proposées

1. **Utilisation de A*** :

   - Ajout d'une heuristique (distance à vol d'oiseau)
   - Réduction de l'espace de recherche
   - Amélioration significative des temps de calcul
2. **Structure de Données Optimisée** :

   - Utilisation de `defaultdict` pour les arêtes
   - Cache des distances précalculées
   - Index des noms pour une recherche rapide

#### Optimisations Futures Suggérées

1. **Prétraitement** :

   - Précalcul des distances fréquemment utilisées
   - Mise en cache des chemins populaires
   - Partitionnement des données pour les grands ensembles
2. **Parallélisation** :

   - Recherche parallèle pour différentes destinations
   - Chargement parallèle des données

## Benchmark et Analyse

### Environnement de Test

- Python 3.12.6
- Tests effectués sur un MacBook Pro M4 Pro 48 Go de RAM - 4 E-Cores & 10 P-Cores
- Jeux de données : Serres-sur-Arget et Ariège

### 4.2 Résultats Comparatifs

#### Performance Temporelle

| Algorithme | Serres-sur-Arget | Ariège |
| ---------- | ---------------- | ------- |
| Dijkstra   | ~2.5ms           | ~15ms   |
| A*         | ~1.8ms           | ~8ms    |

#### Complexité

1. **Complexité Temporelle** :

   - Dijkstra : O(|E| + |V| log |V|)
   - A* : O(|E|) dans le meilleur cas
2. **Complexité Spatiale** :

   - O(|V|) pour les deux algorithmes
   - Structures additionnelles pour A* : négligeable

### 4.3 Analyse des Résultats

1. **Avantages de A*** :

   - 30-45% plus rapide que Dijkstra
   - Particulièrement efficace sur les grands ensembles
   - Même qualité de résultat (chemins optimaux)
2. **Limitations** :

   - Dépendance à la qualité de l'heuristique
   - Surcoût mémoire léger
   - Performance variable selon la topologie du graphe

## 5. Conclusion

L'implémentation de A* apporte une amélioration significative par rapport à Dijkstra, particulièrement sur les grands ensembles de données. Les optimisations de structure de données et l'utilisation d'une heuristique efficace permettent d'obtenir des performances satisfaisantes tout en garantissant l'optimalité des chemins trouvés.

Les perspectives d'amélioration incluent le prétraitement des données et la parallélisation, qui pourraient encore améliorer les performances sur les très grands ensembles de données.
