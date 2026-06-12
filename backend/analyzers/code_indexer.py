"""
Repository code indexer that extracts structure, dependencies, and metrics.
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import ast


@dataclass
class FileInfo:
    """Information about a single file."""
    path: str
    language: str
    size_bytes: int
    lines_of_code: int
    has_tests: bool


@dataclass
class CodeMetrics:
    """Code metrics and statistics."""
    total_files: int
    total_lines: int
    languages: Dict[str, int]
    avg_file_size: float
    has_tests: bool
    complexity_score: float


@dataclass
class DependencyInfo:
    """Information about a module/file dependency."""
    source: str
    target: str
    dependency_type: str  # 'import', 'require', 'http', etc.


class CodeIndexer:
    """
    Indexes a repository to extract structure, files, dependencies, and metrics.
    """

    # File extensions and their language mappings
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.jsx': 'javascript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
    }

    # Directories and files to skip
    SKIP_DIRS = {
        '__pycache__', '.git', 'node_modules', '.venv', 'venv',
        'build', 'dist', '.next', '.nuxt', 'coverage', '.pytest_cache',
        '.idea', '.vscode', 'target', 'bin', 'obj'
    }

    def __init__(self, repo_path: str, max_file_size_mb: int = 50):
        """
        Initialize the code indexer.
        
        Args:
            repo_path: Path to the repository to analyze
            max_file_size_mb: Maximum file size to analyze in MB
        """
        self.repo_path = Path(repo_path)
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        
        self.files: Dict[str, FileInfo] = {}
        self.dependencies: List[DependencyInfo] = []
        self.language_counts: Dict[str, int] = defaultdict(int)
        self.module_structure: Dict[str, List[str]] = defaultdict(list)

    def index(self) -> CodeMetrics:
        """
        Index the entire repository.
        
        Returns:
            CodeMetrics: Aggregated metrics from the analysis
        """
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {self.repo_path}")

        self._scan_files()
        self._extract_dependencies()
        self._build_module_structure()

        return self._compute_metrics()

    def _scan_files(self) -> None:
        """Scan repository and collect file information."""
        for file_path in self.repo_path.rglob('*'):
            # Skip directories and files we don't want
            if file_path.is_dir():
                if any(skip in file_path.parts for skip in self.SKIP_DIRS):
                    continue
                continue

            # Check file size
            if file_path.stat().st_size > self.max_file_size_bytes:
                continue

            # Determine language
            suffix = file_path.suffix.lower()
            language = self.LANGUAGE_MAP.get(suffix)
            if not language:
                continue

            # Count lines of code
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
            except Exception:
                continue

            # Relative path
            rel_path = str(file_path.relative_to(self.repo_path))

            # Check if test file
            is_test = 'test' in rel_path.lower() or rel_path.endswith(('_test.py', '.test.js', '.spec.ts'))

            # Store file info
            self.files[rel_path] = FileInfo(
                path=rel_path,
                language=language,
                size_bytes=file_path.stat().st_size,
                lines_of_code=lines,
                has_tests=is_test
            )

            self.language_counts[language] += 1

    def _extract_dependencies(self) -> None:
        """Extract dependencies from Python and JavaScript files."""
        for file_path, file_info in self.files.items():
            full_path = self.repo_path / file_path

            if file_info.language == 'python':
                self._extract_python_dependencies(full_path, file_path)
            elif file_info.language in ['javascript', 'typescript']:
                self._extract_js_dependencies(full_path, file_path)

    def _extract_python_dependencies(self, file_path: Path, rel_path: str) -> None:
        """Extract imports from Python files."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name.split('.')[0]
                        self.dependencies.append(DependencyInfo(
                            source=rel_path,
                            target=module,
                            dependency_type='import'
                        ))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module.split('.')[0]
                        self.dependencies.append(DependencyInfo(
                            source=rel_path,
                            target=module,
                            dependency_type='import'
                        ))
        except Exception:
            pass

    def _extract_js_dependencies(self, file_path: Path, rel_path: str) -> None:
        """Extract imports from JavaScript/TypeScript files."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            import re
            # Simple regex patterns for JS imports
            patterns = [
                r"import\s+.*?from\s+['\"]([^'\"]+)['\"]",
                r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            ]

            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    module = match.group(1).split('/')[0].split('.')[0]
                    if module and not module.startswith('.'):
                        self.dependencies.append(DependencyInfo(
                            source=rel_path,
                            target=module,
                            dependency_type='import'
                        ))
        except Exception:
            pass

    def _build_module_structure(self) -> None:
        """Build hierarchical module structure."""
        for file_path in self.files.keys():
            parts = Path(file_path).parent.parts
            module = '/'.join(parts) if parts else 'root'
            self.module_structure[module].append(file_path)

    def _compute_metrics(self) -> CodeMetrics:
        """Compute overall code metrics."""
        total_lines = sum(f.lines_of_code for f in self.files.values())
        has_tests = any(f.has_tests for f in self.files.values())

        # Simple complexity score (0-100)
        complexity_score = min(100, len(self.dependencies) / 10)

        return CodeMetrics(
            total_files=len(self.files),
            total_lines=total_lines,
            languages=dict(self.language_counts),
            avg_file_size=sum(f.size_bytes for f in self.files.values()) / len(self.files) if self.files else 0,
            has_tests=has_tests,
            complexity_score=complexity_score
        )

    def get_files(self, language: Optional[str] = None) -> Dict[str, FileInfo]:
        """Get indexed files, optionally filtered by language."""
        if language:
            return {k: v for k, v in self.files.items() if v.language == language}
        return self.files

    def get_dependencies(self, source_file: Optional[str] = None) -> List[DependencyInfo]:
        """Get dependencies, optionally filtered by source file."""
        if source_file:
            return [d for d in self.dependencies if d.source == source_file]
        return self.dependencies

    def get_module_structure(self) -> Dict[str, List[str]]:
        """Get hierarchical module structure."""
        return self.module_structure

    def get_metrics(self) -> CodeMetrics:
        """Get computed metrics."""
        return CodeMetrics(
            total_files=len(self.files),
            total_lines=sum(f.lines_of_code for f in self.files.values()),
            languages=dict(self.language_counts),
            avg_file_size=sum(f.size_bytes for f in self.files.values()) / len(self.files) if self.files else 0,
            has_tests=any(f.has_tests for f in self.files.values()),
            complexity_score=min(100, len(self.dependencies) / 10)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Export indexer state as dictionary."""
        return {
            'files': {k: asdict(v) for k, v in self.files.items()},
            'dependencies': [asdict(d) for d in self.dependencies],
            'module_structure': self.module_structure,
            'metrics': asdict(self.get_metrics())
        }
