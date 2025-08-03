#!/usr/bin/env python3
"""
Project File Usage Analyzer
Analyzes all files in the emergentTrader project to determine:
1. Which files are used/imported/referenced
2. Where they are used
3. File dependencies and relationships
4. Unused files
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict, Counter
import ast

class ProjectAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.file_usage = defaultdict(list)
        self.file_dependencies = defaultdict(set)
        self.all_files = set()
        self.used_files = set()
        self.file_types = Counter()
        
        # Patterns for different types of imports/references
        self.patterns = {
            'python_import': [
                r'from\s+([.\w]+)\s+import',
                r'import\s+([.\w]+)',
                r'__import__\([\'"]([^\'\"]+)[\'"]',
            ],
            'js_import': [
                r'import\s+.*?\s+from\s+[\'"]([^\'\"]+)[\'"]',
                r'require\([\'"]([^\'\"]+)[\'"]\)',
                r'import\([\'"]([^\'\"]+)[\'"]\)',
            ],
            'file_reference': [
                r'[\'"]([^\'\"]*\.(py|js|json|md|txt|csv|sql|sh|yml|yaml))[\'"]',
                r'open\([\'"]([^\'\"]+)[\'"]',
                r'Path\([\'"]([^\'\"]+)[\'"]',
            ],
            'next_js_pages': [
                r'href=[\'"]([^\'\"]+)[\'"]',
                r'router\.push\([\'"]([^\'\"]+)[\'"]',
                r'Link.*?to=[\'"]([^\'\"]+)[\'"]',
            ]
        }
    
    def scan_all_files(self):
        """Scan all files in the project directory"""
        ignore_dirs = {'.git', 'node_modules', '__pycache__', '.next', 'venv', '.idea'}
        ignore_files = {'.DS_Store', '.gitignore'}
        
        for root, dirs, files in os.walk(self.project_root):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file not in ignore_files:
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.project_root)
                    self.all_files.add(str(relative_path))
                    
                    # Count file types
                    suffix = file_path.suffix.lower()
                    self.file_types[suffix] += 1
    
    def analyze_file_content(self, file_path):
        """Analyze a single file for imports and references"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = file_path.relative_to(self.project_root)
            file_ext = file_path.suffix.lower()
            
            # Analyze based on file type
            if file_ext == '.py':
                self.analyze_python_file(content, str(relative_path))
            elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
                self.analyze_js_file(content, str(relative_path))
            elif file_ext in ['.json', '.md', '.txt', '.sh', '.yml', '.yaml']:
                self.analyze_text_file(content, str(relative_path))
                
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def analyze_python_file(self, content, file_path):
        """Analyze Python file for imports and references"""
        # Try AST parsing first for accurate import detection
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.add_dependency(file_path, alias.name, 'python_import')
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.add_dependency(file_path, node.module, 'python_import')
        except:
            # Fallback to regex if AST parsing fails
            pass
        
        # Use regex patterns for additional references
        for pattern_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    self.add_dependency(file_path, match, pattern_type)
    
    def analyze_js_file(self, content, file_path):
        """Analyze JavaScript/TypeScript file for imports and references"""
        for pattern_type, patterns in self.patterns.items():
            if pattern_type in ['js_import', 'file_reference', 'next_js_pages']:
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.MULTILINE)
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]
                        self.add_dependency(file_path, match, pattern_type)
    
    def analyze_text_file(self, content, file_path):
        """Analyze text files for file references"""
        for pattern in self.patterns['file_reference']:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                self.add_dependency(file_path, match, 'file_reference')
    
    def add_dependency(self, source_file, target, dependency_type):
        """Add a dependency relationship"""
        # Clean up the target path
        target = target.strip()
        if not target:
            return
            
        # Convert relative imports to file paths where possible
        if dependency_type == 'python_import':
            # Handle relative imports
            if target.startswith('.'):
                target = self.resolve_relative_import(source_file, target)
            else:
                # Check if it's a local module
                potential_file = target.replace('.', '/') + '.py'
                if potential_file in self.all_files:
                    target = potential_file
        
        elif dependency_type == 'js_import':
            # Handle JS imports
            if target.startswith('./') or target.startswith('../'):
                target = self.resolve_relative_path(source_file, target)
            elif not target.startswith('@') and not target.startswith('http'):
                # Might be a local file
                for ext in ['.js', '.jsx', '.ts', '.tsx']:
                    potential_file = target + ext
                    if potential_file in self.all_files:
                        target = potential_file
                        break
        
        # Record the usage
        self.file_usage[target].append({
            'used_by': source_file,
            'type': dependency_type
        })
        self.file_dependencies[source_file].add(target)
        
        # Mark as used if it exists in our file list
        if target in self.all_files:
            self.used_files.add(target)
    
    def resolve_relative_import(self, source_file, import_path):
        """Resolve Python relative imports"""
        source_dir = Path(source_file).parent
        
        # Count leading dots
        level = 0
        for char in import_path:
            if char == '.':
                level += 1
            else:
                break
        
        # Remove leading dots
        module_path = import_path[level:]
        
        # Go up directories based on level
        target_dir = source_dir
        for _ in range(level - 1):
            target_dir = target_dir.parent
        
        # Construct the target path
        if module_path:
            target_path = target_dir / (module_path.replace('.', '/') + '.py')
        else:
            target_path = target_dir / '__init__.py'
        
        return str(target_path)
    
    def resolve_relative_path(self, source_file, relative_path):
        """Resolve relative file paths"""
        source_dir = Path(source_file).parent
        target_path = (source_dir / relative_path).resolve()
        
        try:
            return str(target_path.relative_to(self.project_root))
        except ValueError:
            return relative_path
    
    def generate_report(self):
        """Generate comprehensive usage report"""
        report = {
            'summary': {
                'total_files': len(self.all_files),
                'used_files': len(self.used_files),
                'unused_files': len(self.all_files) - len(self.used_files),
                'file_types': dict(self.file_types)
            },
            'file_usage': {},
            'unused_files': list(self.all_files - self.used_files),
            'dependencies': {}
        }
        
        # Detailed file usage
        for file_path in sorted(self.all_files):
            usage_info = {
                'is_used': file_path in self.used_files,
                'used_by': self.file_usage.get(file_path, []),
                'depends_on': list(self.file_dependencies.get(file_path, set()))
            }
            report['file_usage'][file_path] = usage_info
        
        return report
    
    def run_analysis(self):
        """Run the complete analysis"""
        print("Scanning all files...")
        self.scan_all_files()
        
        print(f"Found {len(self.all_files)} files")
        print("Analyzing file contents...")
        
        for file_path_str in self.all_files:
            file_path = self.project_root / file_path_str
            if file_path.is_file():
                self.analyze_file_content(file_path)
        
        print("Generating report...")
        return self.generate_report()

def main():
    project_root = "/Users/danishkhan/Development/Clients/emergentTrader"
    analyzer = ProjectAnalyzer(project_root)
    
    report = analyzer.run_analysis()
    
    # Save detailed report
    with open(os.path.join(project_root, 'PROJECT_FILE_USAGE_ANALYSIS.json'), 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate markdown report
    generate_markdown_report(report, project_root)
    
    print(f"\nAnalysis complete!")
    print(f"Total files: {report['summary']['total_files']}")
    print(f"Used files: {report['summary']['used_files']}")
    print(f"Unused files: {report['summary']['unused_files']}")

def generate_markdown_report(report, project_root):
    """Generate a markdown report"""
    md_content = f"""# Project File Usage Analysis Report

## Summary
- **Total Files**: {report['summary']['total_files']}
- **Used Files**: {report['summary']['used_files']}
- **Unused Files**: {report['summary']['unused_files']}
- **Usage Rate**: {(report['summary']['used_files'] / report['summary']['total_files'] * 100):.1f}%

## File Types Distribution
"""
    
    for ext, count in sorted(report['summary']['file_types'].items()):
        md_content += f"- **{ext or 'no extension'}**: {count} files\n"
    
    md_content += "\n## Used Files and Their Dependencies\n\n"
    
    for file_path, info in sorted(report['file_usage'].items()):
        if info['is_used']:
            md_content += f"### {file_path}\n"
            
            if info['used_by']:
                md_content += "**Used by:**\n"
                for usage in info['used_by']:
                    md_content += f"- {usage['used_by']} ({usage['type']})\n"
            
            if info['depends_on']:
                md_content += "**Depends on:**\n"
                for dep in sorted(info['depends_on']):
                    md_content += f"- {dep}\n"
            
            md_content += "\n"
    
    md_content += "\n## Unused Files\n\n"
    
    if report['unused_files']:
        md_content += "The following files appear to be unused:\n\n"
        for file_path in sorted(report['unused_files']):
            md_content += f"- {file_path}\n"
    else:
        md_content += "All files appear to be used!\n"
    
    # Save markdown report
    with open(os.path.join(project_root, 'PROJECT_FILE_USAGE_REPORT.md'), 'w') as f:
        f.write(md_content)

if __name__ == "__main__":
    main()
