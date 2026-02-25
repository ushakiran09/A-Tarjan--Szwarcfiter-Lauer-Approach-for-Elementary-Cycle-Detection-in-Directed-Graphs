import unittest
import importlib.util
import sys
import os

# --- 1. AUTOMATIC DIRECTORY DETECTION ---
# This finds the folder where THIS script (test_trsl.py) is saved
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_name = "TRSL1.py"
full_path = os.path.join(BASE_DIR, file_name)

if not os.path.exists(full_path):
    print(f"Error: Could not find '{file_name}' at {full_path}")
    print(f"Files actually in this folder: {os.listdir(BASE_DIR)}")
    sys.exit(1)

# --- 2. DYNAMIC IMPORT ---
spec = importlib.util.spec_from_file_location("trsl_module", full_path)
trsl_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sl_module if 'sl_module' in locals() else trsl_module)

TarjanPreprocessing = trsl_module.TarjanPreprocessing
SzwarcfiterLauer = trsl_module.SzwarcfiterLauer

class TestAlgorithmOutput(unittest.TestCase):

    def normalize_cycle(self, cycle):
        """Standardizes a cycle so it can be compared regardless of rotation."""
        if not cycle: return tuple()
        path = cycle[:-1]
        min_node = min(path)
        min_index = path.index(min_node)
        rotated = path[min_index:] + path[:min_index]
        return tuple(rotated)

    def test_graph_cycles_match(self):
        # Your specific graph input
        my_graph = {
            "1": ["2"],
            "2": ["1", "3"],
            "3": ["4", "5"],
            "4": ["5"],
            "5": ["3", "6"],
            "6": []
        }

        # Your expected output
        expected_output = [
            ['1', '2', '1'],
            ['3', '4', '5', '3'],
            ['3', '5', '3']
        ]

        # Algorithm logic replication
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

        actual_set = set(self.normalize_cycle(c) for c in actual_cycles)
        expected_set = set(self.normalize_cycle(c) for c in expected_output)

        missing = expected_set - actual_set
        extra = actual_set - expected_set

        error_message = ""
        if missing: error_message += f"\n[MISSING]: {missing}"
        if extra: error_message += f"\n[EXTRA]: {extra}"

        self.assertEqual(actual_set, expected_set, error_message)
        print("\nOK: Algorithm output matches expected cycles perfectly.")

if __name__ == "__main__":
    unittest.main(verbosity=2)