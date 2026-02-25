import unittest
import importlib.util
import sys
import os

# --- 1. DYNAMIC IMPORT OF TRSL1.py ---
# This method is used to safely load the file and its classes
file_name = "TRSL1.py"
if not os.path.exists(file_name):
    print(f"Error: {file_name} not found in the current directory.")
    sys.exit(1)

spec = importlib.util.spec_from_file_location("trsl_module", file_name)
trsl_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trsl_module)

# Pulling the classes from the imported module
TarjanPreprocessing = trsl_module.TarjanPreprocessing
SzwarcfiterLauer = trsl_module.SzwarcfiterLauer

class TestAlgorithmOutput(unittest.TestCase):

    def normalize_cycle(self, cycle):
        """
        Normalizes a cycle so it can be compared regardless of rotation.
        Example: ['2', '1', '2'] becomes ('1', '2')
        """
        if not cycle: return tuple()
        path = cycle[:-1] # Remove the repeated end node
        min_node = min(path)
        min_index = path.index(min_node)
        # Rotate so the smallest node is always first
        rotated = path[min_index:] + path[:min_index]
        return tuple(rotated)

    def test_graph_cycles_match(self):
        # --- A. YOUR INPUT GRAPH ---
        my_graph = {
            "1": ["2"],
            "2": ["1", "3"],
            "3": ["4", "5"],
            "4": ["5"],
            "5": ["3", "6"],
            "6": []
        }

        # --- B. YOUR EXPECTED OUTPUT ---
        # Add or modify the expected cycles here
        expected_output = [
            ['1', '2', '1'],
            ['3', '4', '5', '3'],
            ['3', '5', '3']
        ]

        # --- C. RUN THE ALGORITHM LOGIC ---
        # We replicate the logic inside your run_single_graph function
        tarjan = TarjanPreprocessing(my_graph)
        sccs = tarjan.get_sccs()
        
        actual_cycles = []
        for scc_nodes in sccs:
            if len(scc_nodes) < 2:
                node = scc_nodes[0]
                if node not in my_graph.get(node, []):
                    continue
            
            detector = SzwarcfiterLauer(my_graph, scc_nodes)
            actual_cycles.extend(detector.run())

        # --- D. COMPARE ---
        # Normalize both to sets of tuples to ignore order and rotation
        actual_set = set(self.normalize_cycle(c) for c in actual_cycles)
        expected_set = set(self.normalize_cycle(c) for c in expected_output)

        # Check for differences
        missing = expected_set - actual_set
        extra = actual_set - expected_set

        error_message = ""
        if missing:
            error_message += f"\n[MISSING CYCLES]: {missing}"
        if extra:
            error_message += f"\n[EXTRA CYCLES FOUND]: {extra}"

        # Assert equality
        self.assertEqual(actual_set, expected_set, error_message)
        print("\nOK: Algorithm output matches expected cycles perfectly.")

if __name__ == "__main__":
    unittest.main(verbosity=2)