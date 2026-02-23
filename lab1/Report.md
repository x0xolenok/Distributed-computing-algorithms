# Communication Graph Analysis (Lab 1)

This repository contains a Python implementation for analyzing communication graph structures, specifically focusing on data integrity, symmetry, and tree topology.

## 👤 Author
**Bohdan Khokhlov** Group MD-51

---

## 📋 Task Overview
The goal of this project is to implement functions that validate a `Neighborhood` data structure, defined as:
`Neighborhood = dict[int, set[int]]`

### Implemented Functions:
1. **`isNeighborhoodCorrect`**: Validates if the neighborhood refers to a correctly represented communication graph.
2. **`isUndirected`**: Checks if the graph represents an undirected network (symmetric connections).
3. **`isTree`**: Determines if the graph is an undirected tree (connected and acyclic).

---

## 🛠 Data Model
The graph is represented using the **Neighborhood** type:
* **Key (`int`)**: A unique node identifier (e.g., a processor or network device).
* **Value (`set[int]`)**: A set of adjacent nodes (neighbors).

**Why `set`?** Using sets allows for $O(1)$ connection lookups and inherently prevents duplicate edges between the same pair of vertices.

---

## 🔍 Detailed Analysis

### 1. Data Integrity (`isNeighborhoodCorrect`)
Ensures there are no "dangling references"—situations where a node refers to a neighbor that does not exist in the network keys.
* **Logic**: The function creates a set of all registered nodes and verifies that every neighbor set is a subset of these keys.
* **Complexity**: $O(V + E)$.

### 2. Symmetry Check (`isUndirected`)
Determines if the communication channels are bidirectional: if $u \to v$ exists, $v \to u$ must also exist.
* **Logic**: After verifying integrity, it iterates through all pairs and checks for return links using the `.get()` method.
* **Complexity**: $O(V + E)$.

### 3. Tree Topology (`isTree`)
A graph is a tree if and only if it is connected and acyclic.
* **Cycle Detection**: Implements a recursive **Depth-First Search (DFS)**. It uses a `parent` argument to ignore the immediate back-edge and identifies cycles if it encounters a previously visited node that isn't the parent.
* **Connectivity**: After DFS, the function ensures the number of visited nodes equals the total number of nodes.
* **Complexity**: $O(V + E)$. In a tree, $E = V - 1$, so it simplifies to $O(V)$.

---

## 🧪 Testing Scenarios
The implementation includes coverage for typical network topologies:
1. **Tree Network**: A linear undirected topology. Passes all checks.
2. **Ring Network**: A closed-loop undirected graph. Fails the tree check due to the cycle.
3. **Directed Network**: A graph with one-way connections. Fails the symmetry check.
4. **Broken Network**: Contains a reference to a non-existent node (ID 3). Fails the initial integrity check.

---

## 💡 Conclusion
The chosen data structures (`dict` and `set`) provide optimal execution time for topological property checks. The DFS approach reliably classifies undirected trees in various network configurations.
