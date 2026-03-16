import ast
import os
import csv

OUTPUT = "../data/testcase_module_map.csv"

REPOS = {
    "black": {
        "tests": "../repos/black/tests",
        "src": "../repos/black/src/black",
        "pkg": "black"
    },
    "requests": {
        "tests": "../repos/requests/tests",
        "src": "../repos/requests/src/requests",
        "pkg": "requests"
    },
    "flask": {
        "tests": "../repos/flask/tests",
        "src": "../repos/flask/src/flask",
        "pkg": "flask"
    }
}


# ========= AST VISITOR =========

class TestVisitor(ast.NodeVisitor):
    def __init__(self):
        self.calls = []
        self.imports = {}

    def visit_Import(self, node):
        for alias in node.names:
            self.imports[alias.asname or alias.name] = alias.name

    def visit_ImportFrom(self, node):
        mod = node.module
        for alias in node.names:
            self.imports[alias.asname or alias.name] = mod

    def visit_Call(self, node):
        name = self.resolve(node.func)
        if name:
            self.calls.append(name)
        self.generic_visit(node)

    def resolve(self, node):
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return self.flatten(node)
        return None

    def flatten(self, node):
        parts = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return ".".join(reversed(parts))


# ========= SOURCE INDEX =========

def index_modules(src):
    index = {}
    print(f"Indexing source directory: {src}")
    for root, _, files in os.walk(src):
        for f in files:
            if f.endswith(".py"):
                name = f.replace(".py", "")
                index[name] = os.path.join(root, f)
    print(f"Found {len(index)} modules.") # Debug line
    return index


# ========= TEST ANALYSIS =========

def analyze_test_file(path):
    with open(path, "r", encoding="utf8") as f:
        tree = ast.parse(f.read())

    visitor = TestVisitor()
    visitor.visit(tree)

    imports = visitor.imports

    test_data = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):

            test_visitor = TestVisitor()
            test_visitor.imports = imports  # reuse imports

            test_visitor.visit(node)

            test_data.append(
                (node.name, test_visitor.calls)
            )

    return test_data, imports


# ========= MAPPING LOGIC =========

def map_calls(calls, imports, module_index, pkg_name):

    mapped = set()

    for call in calls:

        base = call.split(".")[0]

        # case 1: direct module match
        if base in module_index:
            mapped.add(module_index[base])
            continue

        # case 2: package call like requests.get
        if base == pkg_name:
            mapped.add(module_index.get("api", None))
            mapped.add(module_index.get("sessions", None))
            continue

        # case 3: imported symbol
        if base in imports:
            imp = imports[base]
            if imp:
                imp_mod = imp.split(".")[-1]
                if imp_mod in module_index:
                    mapped.add(module_index[imp_mod])

    mapped.discard(None)
    return mapped


# ========= MAIN =========

def process_repo(name, cfg, writer):
    print("Processing:", name)

    module_index = index_modules(cfg["src"])

    for root, _, files in os.walk(cfg["tests"]):
        for f in files:
            if f.startswith("test") and f.endswith(".py"):

                path = os.path.join(root, f)
                rel_test_path = os.path.relpath(path, cfg["tests"])
                test_data, imports = analyze_test_file(path)

                for test_name, calls in test_data:
                    modules = map_calls(
                        calls, imports, module_index, cfg["pkg"]
                    )
                    
                    if not modules:
                        writer.writerow([name, rel_test_path, test_name, "UNMAPPED"])
                    else:
                        for m in modules:
                            writer.writerow([name, rel_test_path, test_name, m])


def main():

    os.makedirs("data", exist_ok=True)

    with open(OUTPUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["repo", "test_file", "testcase", "module"])

        for name, cfg in REPOS.items():
            process_repo(name, cfg, writer)

    print("DONE →", OUTPUT)


if __name__ == "__main__":
    main()