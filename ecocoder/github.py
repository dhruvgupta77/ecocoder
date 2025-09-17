import os
import tempfile
import shutil
from github import Github, GithubException

class GitHubRepoAnalyzer:
    def __init__(self, token):
        self.github = Github(token)
        self.temp_dirs = []
    
    def clone_repository(self, repo_path):
        """Clone a GitHub repository to a temporary directory"""
        try:
            # Get repository
            repo = self.github.get_repo(repo_path)
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="ecocoder_")
            self.temp_dirs.append(temp_dir)
            
            # Clone repository (simplified - in reality we'd use gitpython or subprocess)
            # For prototype, we'll just create the directory structure
            print(f"Would clone {repo_path} to {temp_dir}")
            
            # For demo purposes, create some sample files
            self._create_sample_files(temp_dir, repo_path)
            
            return temp_dir
            
        except GithubException as e:
            raise Exception(f"GitHub API error: {e.data.get('message', str(e))}")
    
    def _create_sample_files(self, temp_dir, repo_path):
        """Create sample files for demonstration"""
        # Create a simple Python file
        python_code = """
def calculate_fibonacci(n):
    # Inefficient recursive calculation
    if n <= 1:
        return n
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def process_data(data):
    result = []
    for item in data:
        # Creating unnecessary copies of data
        temp = item.copy()
        for i in range(100):
            # CPU-intensive operation
            temp.value = i * item.value
        result.append(temp)
    return result
"""
        
        os.makedirs(os.path.join(temp_dir, "src"), exist_ok=True)
        with open(os.path.join(temp_dir, "src", "main.py"), "w") as f:
            f.write(python_code)
        
        # Create a test file
        test_code = """
import unittest
from src.main import calculate_fibonacci

class TestFibonacci(unittest.TestCase):
    def test_fibonacci(self):
        self.assertEqual(calculate_fibonacci(0), 0)
        self.assertEqual(calculate_fibonacci(1), 1)
        self.assertEqual(calculate_fibonacci(10), 55)
"""
        
        os.makedirs(os.path.join(temp_dir, "tests"), exist_ok=True)
        with open(os.path.join(temp_dir, "tests", "test_fibonacci.py"), "w") as f:
            f.write(test_code)
    
    def cleanup(self, repo_dir):
        """Clean up temporary directories"""
        try:
            if repo_dir in self.temp_dirs:
                shutil.rmtree(repo_dir)
                self.temp_dirs.remove(repo_dir)
        except:
            pass  # Ignore cleanup errors