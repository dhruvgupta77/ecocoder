# EcoCoder CLI

A command-line tool that analyzes GitHub repositories for carbon emissions and sustainability issues.

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install the package: `pip install -e .`

## Usage

1. Set your GitHub token as an environment variable:
   ```bash
   export GITHUB_TOKEN=your_github_token_here

2. Analyze a repository:
   ```bash
   ecocoder https://github.com/username/repository

3. For more options:
   ```bash
   ecocoder --help

Options

    -o, --output: Output format (text, json, html)

    -d, --detail: Detail level (basic, detailed, comprehensive)

    -t, --token: GitHub personal access token

4. Example
```bash
ecocoder https://github.com/exampleuser/example-repo -o html -d comprehensive
