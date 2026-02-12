import sys
from collections import defaultdict

# Standard recursion limit increase for deep backtracking [cite: 102]
sys.setrecursionlimit(10000)

class SzwarcfiterLauer:
    """
    Implementation of the Szwarcfiter-Lauer algorithm for elementary cycles.
    Optimized for zero duplicates by managing the q-index based on the 
    'never-deleted' status of vertices[cite: 6, 162].
    """

    def __init__(self, graph):
        self.graph = graph
        self.nodes = list(graph.keys())
        self.N = len(self.nodes)
        
        # A: Adjacency lists modified/restored during search [cite: 77, 123]
        self.A = {u: list(v_list) for u, v_list in graph.items()}
        # B: Blocking lists (B(v)) for managing unproductive edges [cite: 69, 104]
        self.B = defaultdict(list)
        
        # State tracking vectors as defined in the paper [cite: 68-73]
        self.mark = {u: False for u in self.nodes}
        self.reach = {u: False for u in self.nodes}
        self.position = {u: 0 for u in self.nodes}
        
        self.stack = []
        self.all_cycles = []

    def _nocycle(self, x, y):
        """Procedure NOCYCLE(x, y): Block edge (x, y) [cite: 103-106]."""
        self.B[y].append(x)
        if y in self.A[x]:
            self.A[x].remove(y)

    def _unmark(self, x):
        """Procedure UNMARK(x): Recursively restore edges and unmark [cite: 107-115]."""
        self.mark[x] = False
        for y in list(self.B[x]):
            self.A[y].append(x)
            if self.mark[y]:
                self._unmark(y)
        self.B[x] = []

    def cycle(self, v, q):
        """
        Recursive procedure CYCLE(v, q; result f) [cite: 102, 116-136].
        """
        f = False
        self.mark[v] = True
        self.stack.append(v)
        
        t = len(self.stack)
        self.position[v] = t
        
        # Paper logic: q identifies the top-most vertex that has never left the stack [cite: 121-122].
        if not self.reach[v]:
            q = t
            
        for w in list(self.A.get(v, [])):
            if w not in self.A[v]: 
                continue
                
            if not self.mark[w]:
                # Standard recursive extension [cite: 124-126]
                if self.cycle(w, q):
                    f = True
                else:
                    self._nocycle(v, w)
            
            elif self.position[w] <= q:
                # NEW elementary cycle detected [cite: 129-130].
                # Extraction occurs only if position(w) <= q to prevent duplicates[cite: 96, 129].
                idx = self.position[w] - 1
                self.all_cycles.append(self.stack[idx:] + [w])
                f = True
            else:
                # Duplicate rotation or unproductive path detection[cite: 97, 131].
                self._nocycle(v, w)
        
        self.stack.pop() # delete v from stack [cite: 132]
        if f:
            self._unmark(v) # if cycle was found, unmark v to allow future paths[cite: 133].
            
        self.reach[v] = True # reach(v) := true [cite: 134]
        self.position[v] = self.N + 1 # sentinel for deleted node [cite: 135]
        return f

    def run(self):
        """
        Processes the graph systematically starting from the vertex 
        with maximal indegree[cite: 78, 212].
        """
        indegrees = {u: 0 for u in self.nodes}
        for u in self.nodes:
            for v in self.graph.get(u, []):
                if v in indegrees:
                    indegrees[v] += 1

        # Sort nodes by maximal indegree heuristic [cite: 78, 212]
        start_candidates = sorted(self.nodes, key=lambda x: indegrees[x], reverse=True)
        
        for s in start_candidates:
            if not self.reach[s]:
                self.cycle(s, 0) # Initial call with q = 0[cite: 139].
                
        return self.all_cycles

# --- Adjacency List Input ---
if __name__ == "__main__":
    # This graph contains several shared edges and overlapping cycles.
    # Node 4 is the bridge between two strongly connected regions.
    input_graph = {
    "1": ["2", "3"],
    "2": ["1", "3"],
    "3": ["4", "1"],
    "4": ["5", "6", "3"],
    "5": ["4", "6"],
    "6": ["3", "4", "5"]
}
    
    detector = SzwarcfiterLauer(input_graph)
    elementary_cycles = detector.run()
    
    print(f"Total Unique Elementary Cycles: {len(elementary_cycles)}")
    for i, path in enumerate(elementary_cycles, 1):
        print(f"Cycle {i}: {' -> '.join(path)}")