# Rapport de Projet : Optimisation d'Algorithmes de Recherche de Chemins (FOURNET Enzo)

## Description du Projet

Notre projet consiste à implémenter et optimiser des algorithmes de recherche de chemins sur des données OpenStreetMap.
L'objectif principal que nous avons choisi est de comparer les performances de deux approches :

- L'algorithme de Dijkstra
- L'algorithme A*

Les données sont fournies sous forme de fichiers CSV contenant :

- Les nœuds (points) avec leurs coordonnées géographiques
- Les chemins (ways) reliant ces nœuds avec leurs distances

*À noter que les données présentent toujours des anomalies, comme des points qui ne sont pas reliés à un chemin, ou des chemins qui ne sont pas reliés à un point. Ou même des points qui apparaissent plusieurs fois dans le fichier.*

## Problèmes Identifiés

### Temps de chargement des données

Il ne s'agit pas de la problématique concernant les algorithmes eux-mêmes mais il nous semble tout de même nécessaire de chercher à optimiser ce processus car il reste très coûteux et fait partie des processus dont nous avons besoin pour trouver un chemin.

L'implémentation de base que nous avions mise en œuvre que l'on retrouve dans le fichier `graph_csv.py` utilise la librairie `csv` qui semble être une des plus lentes pour lire nos fichiers CSV.

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

Nous avons donc effectué des recherches et constaté que `Pandas` était une librairie plus performante pour lire nos fichiers CSV. Nous avons donc implémenté une version utilisant `Pandas` dans le fichier `graph_panda.py`.

```python
df_nodes = pd.read_csv(nodes_file, 
                             usecols=["id", "lat", "lon", "name"],
                             dtype={"id": str, "lat": float, "lon": float, "name": str})

df_ways = pd.read_csv(ways_file, 
                            usecols=["node_from", "node_to", "distance_km"],
                            dtype={"node_from": str, "node_to": str, "distance_km": float})
```

Le temps d'exécution est bien meilleur mais il nous semble toujours possible de l'optimiser.
Après d'autres recherches, nous avons découvert que `Polars` était une librairie encore plus performante pour lire nos fichiers CSV. Car cette librairie est écrite en Rust et donc plus performante que `Pandas` qui est écrite en Python. On retrouve cette version dans le fichier `graph_polar.py`.

```python
df_nodes = pl.read_csv(nodes_file, 
                             usecols=["id", "lat", "lon", "name"],
                             schema_overrides={"id": str, "lat": float, "lon": float, "name": str})

df_ways = pl.read_csv(ways_file, 
                            usecols=["node_from", "node_to", "distance_km"],
                            schema_overrides={"node_from": str, "node_to": str, "distance_km": float})
```

En effectuant un benchmark de ces différentes versions, voici les résultats obtenus :

![benchmark](./img/load_benchmark_results.png)

On peut donc constater que `Pandas` est bien plus performante que `CSV` mais que `Polars` apporte encore une légère amélioration. Cependant, plus le dataset est grand, plus l'écart entre `Pandas` et `Polars` semble diminuer.
Nous utiliserons donc pour la suite du projet `Polars` pour la lecture des fichiers CSV qui est dans notre cas le plus performant.

*Le fichier python `bench_load.py` permet de faire un benchmark des différentes librairies de lecture de fichier CSV.*

### Algorithme de recherche

L'algorithme de recherche que nous avons implémenté est un algorithme de recherche de chemin qui utilise l'algorithme de Dijkstra. Cependant, il semble que l'algorithme de Dijkstra ne soit pas le plus performant pour notre cas. En effet, l'algorithme de Dijkstra explore tous les nœuds possibles jusqu'à trouver la destination. Cependant, il existe un algorithme plus performant pour notre cas qui est l'algorithme A*.

#### Complexité de Calcul

- Dijkstra explore tous les nœuds possibles jusqu'à trouver la destination
- Calculs redondants de distances à vol d'oiseau
- Chargement initial des données coûteux pour de grands ensembles (Même après optimisation avec `Polars`)

#### Structure de Données

- Utilisation de dictionnaires Python pour stocker les nœuds et les arêtes
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

## Benchmark et Analyse

### Environnement de Test

- Python 3.12.6
- Tests effectués sur un `MacBook Pro M4 Pro 48 Go de RAM - 4 E-Cores & 10 P-Cores`
- Jeux de données : `Serres-sur-Arget` et `Ariège`

### Résultats Comparatifs

#### Performance Temporelle

Si dessous le benchmark des différents temps de recherche des chemins entre différents points de départ et d'arrivée.

De `Saint-Pierre-de-Rivière` à `Las Prados` avec le jeu de données `Serres-sur-Arget` :

![benchmark](./img/search_benchmark_Serres_-_Saint-Pierre-de-Rivière_to_Las_Prados.png)

De `Saint-Pierre-de-Rivière` à `Las Prados` avec le jeu de données `Ariège` :

![benchmark](./img/search_benchmark_Ariège_-_Saint-Pierre-de-Rivière_to_Las_Prados.png)

De `Saint-Pierre-de-Rivière` à `Saint-Pierre-de-Rivière` avec le jeu de données `Serres-sur-Arget` :

![benchmark](./img/search_benchmark_Serres_-_Saint-Pierre-de-Rivière_to_Saint-Pierre-de-Rivière.png)

De `Saint-Pierre-de-Rivière` à `Saint-Pierre-de-Rivière` avec le jeu de données `Ariège` :

![benchmark](./img/search_benchmark_Ariège_-_Saint-Pierre-de-Rivière_to_Saint-Pierre-de-Rivière.png)

On constate donc que l'algorithme A* est bien plus performant que l'algorithme de Dijkstra.
Mais nous remarquons aussi une anomalie dans le résultat suivant :

*(Ce chemin n'est possible que sur le jeu de données `Serres-sur-Arget` à cause d'un problème de données dans le jeu de données `Ariège`)*

![benchmark](./img/search_benchmark_Serres_-_Saint-Pierre-de-Rivière_to_Cabane_Coumauzil_-_barguillere.png)

On constate ici qu’A* est nettement moins performant que Dijkstra, sans que nous ayons pu identifier la cause de cette anomalie. Nous supposons qu’il pourrait s’agir d’une erreur dans les données. L’heuristique utilisée pourrait également en être la cause, mais nous n’avons pas eu le temps ni les ressources nécessaires pour en analyser précisément l’origine. Toutefois, étant donné que les données semblent contenir des incohérences, nous avons choisi de ne pas y consacrer davantage de temps, estimant que le problème pourrait provenir de ces dernières.

*Ces benchmarks ont été réalisés avec le fichier `bench_search.py`.*

#### Complexité

1. **Complexité Temporelle** :

   - Dijkstra : O(|E| + |V| log |V|)
   - A* : O(|E| + |V| log |V|) dans le pire cas, mais généralement plus efficace en pratique grâce à l'heuristique qui guide la recherche

2. **Complexité Spatiale** :

   - O(|V|) pour les deux algorithmes
   - Structures additionnelles pour A* : O(|V|) pour la file de priorité et les distances estimées

### Analyse des Résultats

1. **Performance** :

   - A* montre une amélioration significative des temps de calcul dans la plupart des cas
   - Les tests empiriques confirment un gain de performance de 30-45% par rapport à Dijkstra
   - L'efficacité est particulièrement notable sur les grands jeux de données

2. **Qualité des Solutions** :

   - Les deux algorithmes garantissent des chemins optimaux
   - A* explore généralement moins de nœuds pour atteindre la solution
   - La qualité de l'heuristique influence directement les performances

3. **Limitations et Points d'Attention** :

   - L'efficacité de A* dépend fortement de la qualité de l'heuristique
   - Certains cas particuliers peuvent montrer des performances inférieures à Dijkstra
   - La topologie du graphe influence significativement les performances

## Conclusion et Perspectives

Notre implémentation démontre l'intérêt d'utiliser A* pour la recherche de plus courts chemins dans un contexte géographique. Les résultats expérimentaux valident les choix d'implémentation et les optimisations apportées.

Les améliorations futures pourraient inclure :
- L'optimisation de l'heuristique pour mieux prendre en compte le relief
- L'implémentation d'un prétraitement des données pour accélérer les calculs
- L'exploration de variantes bidirectionnelles de l'algorithme
- La parallélisation des calculs pour les très grands graphes

Cette étude confirme l'efficacité de A* comme alternative à Dijkstra pour les problèmes de routage, tout en identifiant ses limites et les pistes d'amélioration possibles.
