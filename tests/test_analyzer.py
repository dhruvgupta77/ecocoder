import unittest
import os
import tempfile
import ast
from ecocoder.analyzer import CodeAnalyzer, PythonASTAnalyzer


class TestCodeAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CodeAnalyzer()
        self.ast_analyzer = PythonASTAnalyzer()

    def test_analyze_python_file_with_issues(self):
        """Test analyzing a Python file with known sustainability issues"""
        # Create a temporary Python file with issues
        test_code = '''
def example_function():
    # Nested loops - should be flagged
    result = []
    for i in range(10):
        for j in range(10):
            result.append(i * j)
    return result

def recursive_function(n):
    # Recursion without base case - should be flagged
    if n <= 0:
        return 1
    return n * recursive_function(n-1)

def data_processing(data):
    # Unnecessary copying - should be flagged
    import copy
    new_data = copy.deepcopy(data)
    return new_data

def direct_deepcopy(data):
    # Direct deepcopy import - should be flagged
    from copy import deepcopy
    return deepcopy(data)
'''
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Analyze the file
            issues = self.analyzer._analyze_python_file(temp_file)
            
            # Should find at least 3 issues (nested loops, recursion, and at least one deepcopy)
            self.assertGreaterEqual(len(issues), 3)
            
            # Check that specific issues are detected
            issue_types = [issue['issue'] for issue in issues]
            self.assertTrue(any('Nested loops' in issue for issue in issue_types))
            self.assertTrue(any('Recursive function' in issue for issue in issue_types))
            self.assertTrue(any('Deep copy' in issue for issue in issue_types))
            
        finally:
            # Clean up
            os.unlink(temp_file)

    def test_analyze_python_file_without_issues(self):
        """Test analyzing a Python file without obvious issues"""
        # Create a temporary Python file without obvious issues
        test_code = '''
def efficient_function(data):
    # Simple function without obvious issues
    return [x * 2 for x in data]

def process_items(items):
    # Using a generator expression for memory efficiency
    return (item.process() for item in items)
'''
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Analyze the file
            issues = self.analyzer._analyze_python_file(temp_file)
            
            # Should find few or no issues
            self.assertLessEqual(len(issues), 1)  # Allow for false positives
            
        finally:
            # Clean up
            os.unlink(temp_file)

    def test_ast_analyzer_nested_loops(self):
        """Test AST analyzer with nested loops"""
        code = """
for i in range(10):
    for j in range(10):
        print(i * j)
"""
        tree = ast.parse(code)
        issues = self.ast_analyzer.analyze(tree, "test.py")
        
        # Should detect nested loops
        self.assertEqual(len(issues), 1)
        self.assertIn("Nested loops", issues[0]['issue'])

    def test_ast_analyzer_recursion(self):
        """Test AST analyzer with recursion"""
        code = """
def factorial(n):
    return n * factorial(n-1)
"""
        tree = ast.parse(code)
        issues = self.ast_analyzer.analyze(tree, "test.py")
        
        # Should detect recursion
        self.assertEqual(len(issues), 1)
        self.assertIn("Recursive function", issues[0]['issue'])

    def test_ast_analyzer_deepcopy_attribute(self):
        """Test AST analyzer with copy.deepcopy()"""
        code = """
import copy
def process_data(data):
    return copy.deepcopy(data)
"""
        tree = ast.parse(code)
        issues = self.ast_analyzer.analyze(tree, "test.py")
        
        # Should detect deepcopy
        self.assertEqual(len(issues), 1)
        self.assertIn("Deep copy", issues[0]['issue'])

    def test_ast_analyzer_deepcopy_direct(self):
        """Test AST analyzer with direct deepcopy import"""
        code = """
from copy import deepcopy
def process_data(data):
    return deepcopy(data)
"""
        tree = ast.parse(code)
        issues = self.ast_analyzer.analyze(tree, "test.py")
        
        # Should detect deepcopy
        self.assertEqual(len(issues), 1)
        self.assertIn("Deep copy", issues[0]['issue'])

    def test_calculate_emissions(self):
        """Test emissions calculation"""
        analysis_result = {
            "total_lines": 100,
            "issues_found": [
                {"issue": "Test issue", "file": "test.py", "line": 1, "severity": "warning"}
            ],
            "metrics": {
                "cpu_intensive_operations": 5,
                "memory_inefficiencies": 3,
                "network_calls": 2,
                "database_queries": 0,
                "file_operations": 1,
                "complexity_score": 2.5
            }
        }
        
        emissions_report = self.analyzer.calculate_emissions(analysis_result)
        
        # Should have expected structure
        self.assertIn("total_emissions_kgco2e", emissions_report)
        self.assertIn("breakdown", emissions_report)
        self.assertIn("analysis_result", emissions_report)
        
        # Emissions should be positive
        self.assertGreater(emissions_report["total_emissions_kgco2e"], 0)

    def test_find_code_files(self):
        """Test finding code files in a directory"""
        # Create a temporary directory with various files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Python files
            with open(os.path.join(temp_dir, "test1.py"), "w") as f:
                f.write("print('test')")
            with open(os.path.join(temp_dir, "test2.js"), "w") as f:
                f.write("console.log('test')")
            with open(os.path.join(temp_dir, "test3.java"), "w") as f:
                f.write("class Test {}")
            with open(os.path.join(temp_dir, "README.md"), "w") as f:
                f.write("# Test Project")
            
            # Find code files
            code_files = self.analyzer._find_code_files(temp_dir)
            
            # Should find 3 code files, but not the README
            self.assertEqual(len(code_files), 3)
            self.assertTrue(any(f.endswith('.py') for f in code_files))
            self.assertTrue(any(f.endswith('.js') for f in code_files))
            self.assertTrue(any(f.endswith('.java') for f in code_files))
            self.assertFalse(any(f.endswith('.md') for f in code_files))

    def test_analyze_repository(self):
        """Test analyzing a repository"""
        # Create a temporary directory with some code files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Python file with issues
            with open(os.path.join(temp_dir, "test.py"), "w") as f:
                f.write("""
def inefficient_function():
    result = []
    for i in range(100):
        for j in range(100):
            result.append(i * j)
    return result
""")
            
            # Create JavaScript file
            with open(os.path.join(temp_dir, "test.js"), "w") as f:
                f.write("console.log('Hello World');")
            
            # Analyze the repository
            result = self.analyzer.analyze_repository(temp_dir)
            
            # Should have expected structure
            self.assertIn("files_analyzed", result)
            self.assertIn("total_lines", result)
            self.assertIn("issues_found", result)
            self.assertIn("language_breakdown", result)
            self.assertIn("metrics", result)
            
            # Should find at least 2 files
            self.assertEqual(result["files_analyzed"], 2)
            
            # Should find at least one issue (nested loops)
            self.assertGreaterEqual(len(result["issues_found"]), 1)

    def test_calculate_complexity_score(self):
        """Test complexity score calculation"""
        analysis_result = {
            "total_lines": 500,
            "issues_found": [{"issue": "test"} for _ in range(10)],
            "language_breakdown": {".py": 3, ".js": 2}
        }
        
        score = self.analyzer._calculate_complexity_score(analysis_result)
        
        # Score should be between 0 and 10
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)
        
        # With these inputs, score should be around:
        # 10 issues * 0.5 = 5
        # 500 lines / 1000 = 0.5
        # 2 languages * 0.2 = 0.4
        # Total = 5.9
        self.assertAlmostEqual(score, 5.9, delta=0.1)

    def test_analyze_non_python_file(self):
        """Test analyzing a non-Python file"""
        # Create a temporary JavaScript file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write("console.log('Hello World');")
            temp_file = f.name
        
        try:
            # Analyze the file
            issues = self.analyzer._analyze_file(temp_file)
            
            # Should return a placeholder issue for unsupported language
            self.assertEqual(len(issues), 1)
            self.assertIn("Language-specific analysis", issues[0]['issue'])
            
        finally:
            # Clean up
            os.unlink(temp_file)

    def test_analyze_invalid_python_file(self):
        """Test analyzing an invalid Python file"""
        # Create a temporary file with invalid Python syntax
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def invalid syntax here")
            temp_file = f.name
        
        try:
            # Analyze the file
            issues = self.analyzer._analyze_python_file(temp_file)
            
            # Should return an error issue
            self.assertEqual(len(issues), 1)
            self.assertIn("Error analyzing file", issues[0]['issue'])
            
        finally:
            # Clean up
            os.unlink(temp_file)


class TestPythonASTAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = PythonASTAnalyzer()

    def test_visit_for_nested_loops(self):
        """Test detecting nested loops in for statements"""
        code = """
for i in range(10):
    for j in range(10):
        print(i * j)
"""
        tree = ast.parse(code)
        issues = self.analyzer.analyze(tree, "test.py")
        
        self.assertEqual(len(issues), 1)
        self.assertIn("Nested loops", issues[0]['issue'])

    def test_visit_call_deepcopy_attribute(self):
        """Test detecting copy.deepcopy() calls"""
        code = """
import copy
def test():
    return copy.deepcopy([1, 2, 3])
"""
        tree = ast.parse(code)
        issues = self.analyzer.analyze(tree, "test.py")
        
        self.assertEqual(len(issues), 1)
        self.assertIn("Deep copy", issues[0]['issue'])

    def test_visit_call_deepcopy_direct(self):
        """Test detecting direct deepcopy() calls"""
        code = """
from copy import deepcopy
def test():
    return deepcopy([1, 2, 3])
"""
        tree = ast.parse(code)
        issues = self.analyzer.analyze(tree, "test.py")
        
        self.assertEqual(len(issues), 1)
        self.assertIn("Deep copy", issues[0]['issue'])

    def test_visit_functiondef_recursion(self):
        """Test detecting recursive functions"""
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
        tree = ast.parse(code)
        issues = self.analyzer.analyze(tree, "test.py")
        
        self.assertEqual(len(issues), 1)
        self.assertIn("Recursive function", issues[0]['issue'])

    def test_no_issues_found(self):
        """Test code with no detectable issues"""
        code = """
def simple_function(x):
    return x * 2
"""
        tree = ast.parse(code)
        issues = self.analyzer.analyze(tree, "test.py")
        
        self.assertEqual(len(issues), 0)

    def test_multiple_issues(self):
        """Test code with multiple issues"""
        code = """
def problematic_function(data):
    # Nested loops
    result = []
    for i in range(10):
        for j in range(10):
            result.append(i * j)
    
    # Recursion
    def recursive_helper(n):
        if n <= 0:
            return 1
        return n * recursive_helper(n-1)
    
    # Deep copy
    import copy
    copied_data = copy.deepcopy(data)
    
    return result, recursive_helper(5), copied_data
"""
        tree = ast.parse(code)
        issues = self.analyzer.analyze(tree, "test.py")
        
        # Should find at least 3 issues
        self.assertGreaterEqual(len(issues), 3)
        
        issue_types = [issue['issue'] for issue in issues]
        self.assertTrue(any('Nested loops' in issue for issue in issue_types))
        self.assertTrue(any('Recursive function' in issue for issue in issue_types))
        self.assertTrue(any('Deep copy' in issue for issue in issue_types))


if __name__ == '__main__':
    unittest.main()