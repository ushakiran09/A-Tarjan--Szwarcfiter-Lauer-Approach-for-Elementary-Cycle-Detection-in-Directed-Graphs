import sys
import tomli as tomllib  # Use 'import tomli as tomllib' if Python version < 3.11
from collections import defaultdict

# Standard recursion limit increase for deep backtracking
sys.setrecursionlimit(10000)

class SzwarcfiterLauer:
    """
    Implementation of the Szwarcfiter-Lauer algorithm for elementary cycles.
    Optimized for zero duplicates by managing the q-index based on the 
    'never-deleted' status of vertices.
    """

    def __init__(self, graph):
        self.graph = graph
        self.nodes = list(graph.keys())
        self.N = len(self.nodes)
        
        # A: Adjacency lists modified/restored during search
        self.A = {u: list(v_list) for u, v_list in graph.items()}
        # B: Blocking lists (B(v)) for managing unproductive edges
        self.B = defaultdict(list)
        
        # State tracking vectors 
        self.mark = {u: False for u in self.nodes}
        self.reach = {u: False for u in self.nodes}
        self.position = {u: 0 for u in self.nodes}
        
        self.stack = []
        self.all_cycles = []

    def _nocycle(self, x, y):
        """Procedure NOCYCLE(x, y): Block edge (x, y)."""
        self.B[y].append(x)
        if y in self.A[x]:
            self.A[x].remove(y)

    def _unmark(self, x):
        """Procedure UNMARK(x): Recursively restore edges and unmark."""
        self.mark[x] = False
        for y in list(self.B[x]):
            self.A[y].append(x)
            if self.mark[y]:
                self._unmark(y)
        self.B[x] = []

    def cycle(self, v, q):
        """Recursive procedure CYCLE(v, q; result f)."""
        f = False
        self.mark[v] = True
        self.stack.append(v)
        
        t = len(self.stack)
        self.position[v] = t
        
        if not self.reach[v]:
            q = t
            
        for w in list(self.A.get(v, [])):
            if w not in self.A[v]: 
                continue
                
            if not self.mark[w]:
                if self.cycle(w, q):
                    f = True
                else:
                    self._nocycle(v, w)
            
            elif self.position[w] <= q:
                idx = self.position[w] - 1
                self.all_cycles.append(self.stack[idx:] + [w])
                f = True
            else:
                self._nocycle(v, w)
        
        self.stack.pop() 
        if f:
            self._unmark(v) 
            
        self.reach[v] = True 
        self.position[v] = self.N + 1 
        return f

    def run(self):
        """Processes the graph systematically starting from vertex with max indegree."""
        indegrees = {u: 0 for u in self.nodes}
        for u in self.nodes:
            for v in self.graph.get(u, []):
                if v in indegrees:
                    indegrees[v] += 1

        start_candidates = sorted(self.nodes, key=lambda x: indegrees[x], reverse=True)
        
        for s in start_candidates:
            if not self.reach[s]:
                self.cycle(s, 0)
                
        return self.all_cycles

def run_all_graphs_from_toml(file_path):
    """Loads TOML file and processes each graph independently."""
    try:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return

    graphs = data.get("graphs", {})
    
    if not graphs:
        print("No graphs found in the TOML file under the [graphs] header.")
        return

    for name, adj_list in graphs.items():
        print(f"\n--- Processing Graph: {name} ---")
        
        detector = SzwarcfiterLauer(adj_list)
        results = detector.run()
        
        print(f"Total Unique Elementary Cycles: {len(results)}")
        for i, path in enumerate(results, 1):
            print(f"Cycle {i}: {' -> '.join(path)}")

if __name__ == "__main__":
    # Specify the name of your TOML file here
    run_all_graphs_from_toml("test.toml")