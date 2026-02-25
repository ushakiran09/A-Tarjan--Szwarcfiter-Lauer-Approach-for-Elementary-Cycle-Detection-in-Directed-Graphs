import sys
import tomli as tomllib
from collections import defaultdict

sys.setrecursionlimit(10000)

class TarjanPreprocessing:
    """
    Identifies Strongly Connected Components (SCCs) in a graph.
    Only components with more than one node (or a self-loop) can contain cycles.
    """
    def __init__(self, graph):
        self.graph = graph
        self.index = 0
        self.stack = []
        self.indices = {}
        self.lowlink = {}
        self.on_stack = set()
        self.sccs = []

    def get_sccs(self):
        for node in self.graph:
            if node not in self.indices:
                self._strongconnect(node)
        return self.sccs

    def _strongconnect(self, v):
        self.indices[v] = self.index
        self.lowlink[v] = self.index
        self.index += 1
        self.stack.append(v)
        self.on_stack.add(v)

        for w in self.graph.get(v, []):
            if w not in self.indices:
                self._strongconnect(w)
                self.lowlink[v] = min(self.lowlink[v], self.lowlink[w])
            elif w in self.on_stack:
                self.lowlink[v] = min(self.lowlink[v], self.indices[w])

        if self.lowlink[v] == self.indices[v]:
            scc = []
            while True:
                w = self.stack.pop()
                self.on_stack.remove(w)
                scc.append(w)
                if w == v: break
            self.sccs.append(scc)

class SzwarcfiterLauer:
    def __init__(self, graph, nodes_subset):
        self.nodes = nodes_subset
        self.N = len(self.nodes)
        
        # A: Only include edges where both nodes are in the same SCC
        self.A = defaultdict(list)
        for u in self.nodes:
            for v in graph.get(u, []):
                if v in self.nodes:
                    self.A[u].append(v)
        
        self.B = defaultdict(list)
        self.mark = {u: False for u in self.nodes}
        self.reach = {u: False for u in self.nodes}
        self.position = {u: 0 for u in self.nodes}
        self.stack = []
        self.all_cycles = []

    def _nocycle(self, x, y):
        self.B[y].append(x)
        if y in self.A[x]: self.A[x].remove(y)

    def _unmark(self, x):
        self.mark[x] = False
        for y in list(self.B[x]):
            self.A[y].append(x)
            if self.mark[y]: self._unmark(y)
        self.B[x] = []

    def cycle(self, v, q):
        f = False
        self.mark[v] = True
        self.stack.append(v)
        t = len(self.stack)
        self.position[v] = t
        
        if not self.reach[v]: q = t
            
        for w in list(self.A.get(v, [])):
            if w not in self.A[v]: continue
                
            if not self.mark[w]:
                if self.cycle(w, q): f = True
                else: self._nocycle(v, w)
            elif self.position[w] <= q:
                idx = self.position[w] - 1
                self.all_cycles.append(self.stack[idx:] + [w])
                f = True
            else:
                self._nocycle(v, w)
        
        self.stack.pop() 
        if f: self._unmark(v) 
        self.reach[v] = True 
        self.position[v] = self.N + 1 
        return f

    def run(self):
        # Maximal indegree heuristic within the SCC
        indegrees = {u: 0 for u in self.nodes}
        for u in self.nodes:
            for v in self.A[u]:
                indegrees[v] += 1

        start_candidates = sorted(self.nodes, key=lambda x: indegrees[x], reverse=True)
        for s in start_candidates:
            if not self.reach[s]:
                self.cycle(s, 0)
        return self.all_cycles

def run_all_graphs_from_toml(file_path):
    try:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return

    graphs = data.get("graphs", {})
    for name, full_graph in graphs.items():
        print(f"\n--- Processing Graph: {name} ---")
        
        # 1. TARJAN PREPROCESSING
        tarjan = TarjanPreprocessing(full_graph)
        sccs = tarjan.get_sccs()
        
        total_cycles = []
        for scc_nodes in sccs:
            # Skip SCCs that are single nodes with no self-loop (cannot have cycles)
            if len(scc_nodes) < 2:
                node = scc_nodes[0]
                if node not in full_graph.get(node, []):
                    continue
            
            # 2. RUN SL ON EACH SCC
            detector = SzwarcfiterLauer(full_graph, scc_nodes)
            total_cycles.extend(detector.run())
        
        print(f"Total Unique Elementary Cycles: {len(total_cycles)}")
        for i, path in enumerate(total_cycles, 1):
            print(f"Cycle {i}: {' -> '.join(path)}")

if __name__ == "__main__":
    run_all_graphs_from_toml("test.toml")