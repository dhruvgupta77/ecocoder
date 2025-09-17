import os
import ast
import glob
from typing import Dict, List, Any

class CodeAnalyzer:
    def __init__(self):
        self.metrics = {
            "cpu_intensive_operations": 0,
            "memory_inefficiencies": 0,
            "network_calls": 0,
            "database_queries": 0,
            "file_operations": 0,
            "complexity_score": 0,
        }
        
        # Patterns to look for
        self.cpu_intensive_patterns = [
            "deepcopy", "recursion", "nested loops", "complex algorithms"
        ]
        
        self.memory_inefficient_patterns = [
            "large data structures", "unnecessary copies", "caching missing"
        ]
        
        self.network_call_patterns = [
            "requests.get", "requests.post", "http.client", "urllib.request"
        ]
    
    def analyze_repository(self, repo_dir: str) -> Dict[str, Any]:
        """Analyze a code repository for sustainability issues"""
        results = {
            "files_analyzed": 0,
            "total_lines": 0,
            "language_breakdown": {},
            "issues_found": [],
            "metrics": self.metrics.copy()
        }
        
        # Find all code files
        code_files = self._find_code_files(repo_dir)
        
        for file_path in code_files:
            results["files_analyzed"] += 1
            file_issues = self._analyze_file(file_path)
            results["issues_found"].extend(file_issues)
            
            # Update language stats
            ext = os.path.splitext(file_path)[1]
            results["language_breakdown"][ext] = results["language_breakdown"].get(ext, 0) + 1
            
            # Count lines
            with open(file_path, "r") as f:
                results["total_lines"] += len(f.readlines())
        
        # Calculate complexity score
        results["metrics"]["complexity_score"] = self._calculate_complexity_score(results)
        
        return results
    
    def _find_code_files(self, repo_dir: str) -> List[str]:
        """Find all code files in the repository"""
        code_extensions = [".py", ".js", ".java", ".c", ".cpp", ".cs", ".go", ".rs", ".php", ".rb", ".ts"]
        code_files = []
        
        for ext in code_extensions:
            code_files.extend(glob.glob(os.path.join(repo_dir, "**", f"*{ext}"), recursive=True))
        
        return code_files
    
    def _analyze_file(self, file_path: str) -> List[Dict]:
        """Analyze a single file for sustainability issues"""
        issues = []
        ext = os.path.splitext(file_path)[1]
        
        if ext == ".py":
            return self._analyze_python_file(file_path)
        else:
            # For other languages, we'd implement specific analyzers
            # For now, return a placeholder issue
            issues.append({
                "file": file_path,
                "line": 1,
                "issue": "Language-specific analysis not yet implemented",
                "severity": "info",
                "suggestion": "Consider contributing to EcoCoder to add support for this language"
            })
        
        return issues
    
    def _analyze_python_file(self, file_path: str) -> List[Dict]:
        """Analyze a Python file for sustainability issues"""
        issues = []
        
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Analyze AST for issues
            analyzer = PythonASTAnalyzer()
            issues = analyzer.analyze(tree, file_path)
            
            # Update metrics based on issues found
            for issue in issues:
                if "Nested loops" in issue["issue"] or "Recursive function" in issue["issue"]:
                    self.metrics["cpu_intensive_operations"] += 1
                elif "Deep copy" in issue["issue"]:
                    self.metrics["memory_inefficiencies"] += 1
            
        except Exception as e:
            issues.append({
                "file": file_path,
                "line": 1,
                "issue": f"Error analyzing file: {str(e)}",
                "severity": "error"
            })
        
        return issues
    
    def _calculate_complexity_score(self, results: Dict) -> float:
        """Calculate a complexity score based on the analysis"""
        # Simple heuristic for demo purposes
        complexity = 0
        complexity += len(results["issues_found"]) * 0.5
        complexity += results["total_lines"] / 1000
        complexity += len(results["language_breakdown"]) * 0.2
        
        return min(complexity, 10)  # Cap at 10
    
    def calculate_emissions(self, analysis_result: Dict) -> Dict:
        """Calculate carbon emissions based on code analysis"""
        # Simplified calculation for prototype
        # In a real implementation, this would use more sophisticated models
        
        # Base emissions per line of code
        emissions_per_line = 0.0001  # kgCO2e per line (example value)
        
        # Adjust based on issues found
        issue_multiplier = 1 + (len(analysis_result["issues_found"]) * 0.1)
        
        # Calculate total estimated emissions
        total_emissions = analysis_result["total_lines"] * emissions_per_line * issue_multiplier
        
        # Create emissions report
        emissions_report = {
            "total_emissions_kgco2e": total_emissions,
            "emissions_per_line": emissions_per_line,
            "lines_of_code": analysis_result["total_lines"],
            "issue_multiplier": issue_multiplier,
            "breakdown": {
                "cpu_operations": analysis_result["metrics"]["cpu_intensive_operations"] * 0.01,
                "memory_operations": analysis_result["metrics"]["memory_inefficiencies"] * 0.005,
                "network_operations": analysis_result["metrics"]["network_calls"] * 0.02,
            },
            "analysis_result": analysis_result
        }
        
        return emissions_report

class PythonASTAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
    
    def analyze(self, tree, file_path):
        self.file_path = file_path
        self.visit(tree)
        return self.issues
    
    def visit_For(self, node):
        # Check for nested loops
        for child in ast.walk(node):
            if isinstance(child, ast.For) and child != node:
                self.issues.append({
                    "file": self.file_path,
                    "line": node.lineno,
                    "issue": "Nested loops can be CPU intensive",
                    "severity": "warning",
                    "suggestion": "Consider using more efficient algorithms or vectorization"
                })
                break
        
        self.generic_visit(node)
    
    def visit_Call(self, node):
        # Check for potentially expensive operations
        # Handle direct function calls (e.g., deepcopy())
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name == "deepcopy":
                self.issues.append({
                    "file": self.file_path,
                    "line": node.lineno,
                    "issue": "Deep copy operations can be memory intensive",
                    "severity": "warning",
                    "suggestion": "Consider using shallow copies or references where possible"
                })
        
        # Handle method calls (e.g., copy.deepcopy())
        elif isinstance(node.func, ast.Attribute):
            if (isinstance(node.func.value, ast.Name) and 
                node.func.value.id == "copy" and 
                node.func.attr == "deepcopy"):
                self.issues.append({
                    "file": self.file_path,
                    "line": node.lineno,
                    "issue": "Deep copy operations can be memory intensive",
                    "severity": "warning",
                    "suggestion": "Consider using shallow copies or references where possible"
                })
        
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        # Check for recursion
        for call in ast.walk(node):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name):
                if call.func.id == node.name:
                    self.issues.append({
                        "file": self.file_path,
                        "line": node.lineno,
                        "issue": "Recursive function can be CPU intensive for large inputs",
                        "severity": "warning",
                        "suggestion": "Consider using iterative approaches or memoization"
                    })
                    break
        
        self.generic_visit(node)