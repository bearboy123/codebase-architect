"""
Performance Agent - Detects inefficient code paths and scalability concerns.
"""
import re
from typing import Dict, List

from semantic_kernel import Kernel

from backend.agents.base_agent import BaseAgent, AnalysisResult
from backend.analyzers.code_indexer import CodeIndexer


class PerformanceAgent(BaseAgent):
    """
    Analyzes code for performance issues and scalability concerns.
    
    Detects:
    - N+1 query patterns
    - Inefficient loops and nested iterations
    - Synchronous blocking operations
    - Memory inefficiencies
    - Unoptimized algorithms
    """

    # Performance anti-patterns
    ANTI_PATTERNS = {
        'nested_loops': r'for\s+\w+\s+in\s+.*?:\s*\n\s*for\s+\w+\s+in',
        'n_plus_one': r'for\s+\w+\s+in\s+.*?:\s*(?:.*?\n\s*)*?(?:query|select|find|fetch)\(',
        'sleep_in_loop': r'(?:for|while)\s*.*?:\s*(?:.*?\n\s*)*?(?:sleep|time\.sleep)',
        'large_object_copy': r'= list\(|= dict\(|= \[.*?\].*?\n.*?\n.*?\n',
        'sync_operations': r'\.get\(|requests\.get|requests\.post',
    }

    COMPLEXITY_PATTERNS = {
        'deep_nesting': r'^\s{32,}',  # More than 8 levels of indentation
        'large_function': r'def\s+\w+.*?:\s*(?:\n\s+[^(return)].*?){50,}',
        'long_file': r'',  # Checked separately
    }

    @property
    def agent_name(self) -> str:
        return "Performance Agent"

    @property
    def agent_type(self) -> str:
        return "performance"

    @property
    def description(self) -> str:
        return "Detects inefficient code paths and scalability concerns"

    async def analyze(self) -> AnalysisResult:
        """Perform performance analysis."""
        self.result = AnalysisResult(
            agent_name=self.agent_name,
            agent_type=self.agent_type
        )

        try:
            # Analyze code metrics
            await self._analyze_code_metrics()

            # Scan for anti-patterns
            await self._scan_for_anti_patterns()

            # Check for scalability issues
            await self._check_scalability()

            # Identify optimization opportunities
            await self._identify_optimizations()

            self.result.status = "success"
        except Exception as e:
            self.result.status = "error"
            self.result.error_message = str(e)

        return self.result

    async def _analyze_code_metrics(self) -> None:
        """Analyze code metrics for performance concerns."""
        files = self.indexer.get_files()
        metrics = self.indexer.get_metrics()

        # Check file sizes
        large_files = [f for f in files.values() if f.lines_of_code > 500]
        if large_files:
            self.add_finding(
                title="Large Files Detected",
                description=f"Found {len(large_files)} file(s) with >500 lines. Large files are harder to optimize and maintain.",
                severity="medium",
                details={'large_files': [f.path for f in large_files[:5]]}
            )
        else:
            self.add_recommendation("File sizes are reasonable for optimization.")

        # Check average metrics
        if metrics.total_files > 0:
            avg_lines = metrics.total_lines / metrics.total_files
            if avg_lines > 300:
                self.add_finding(
                    title="High Average File Size",
                    description=f"Average file has {avg_lines:.0f} lines. Consider breaking into smaller modules.",
                    severity="low"
                )

        self.result.metadata['avg_file_size_lines'] = metrics.total_lines / metrics.total_files if metrics.total_files else 0
        self.result.metadata['total_lines'] = metrics.total_lines

    async def _scan_for_anti_patterns(self) -> None:
        """Scan for performance anti-patterns."""
        files = self.indexer.get_files('python')  # Focus on Python for now
        if not files:
            files = self.indexer.get_files('javascript')

        anti_patterns_found = {}

        for file_path, file_info in files.items():
            try:
                full_path = self.indexer.repo_path / file_path
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern_name, pattern in self.ANTI_PATTERNS.items():
                    matches = len(re.findall(pattern, content, re.MULTILINE))
                    if matches > 0:
                        if pattern_name not in anti_patterns_found:
                            anti_patterns_found[pattern_name] = []
                        anti_patterns_found[pattern_name].append((file_path, matches))

            except Exception:
                continue

        # Report findings
        for pattern_name, occurrences in anti_patterns_found.items():
            total = sum(count for _, count in occurrences)
            severity = "high" if pattern_name in ['n_plus_one', 'nested_loops'] else "medium"

            self.add_finding(
                title=f"Performance Anti-Pattern: {pattern_name.replace('_', ' ').title()}",
                description=f"Found {total} occurrence(s) of {pattern_name}. This may impact performance.",
                severity=severity,
                details={'affected_files': occurrences[:3]}
            )

        if not anti_patterns_found:
            self.add_recommendation("No obvious performance anti-patterns detected.")

        self.result.metadata['anti_patterns_found'] = list(anti_patterns_found.keys())

    async def _check_scalability(self) -> None:
        """Check for scalability concerns."""
        files = self.indexer.get_files()
        metrics = self.indexer.get_metrics()

        # Complexity score based on dependencies
        complexity_score = metrics.complexity_score

        if complexity_score > 80:
            self.add_finding(
                title="High Code Complexity",
                description="Complex dependencies may affect scalability. Consider refactoring.",
                severity="medium"
            )
        elif complexity_score > 50:
            self.add_finding(
                title="Moderate Complexity",
                description="Code has moderate complexity. Monitor for scalability issues.",
                severity="low"
            )
        else:
            self.add_recommendation("Code complexity is reasonable for scalability.")

        # Check for database-related operations
        db_operations = 0
        for file_path in files.keys():
            if any(db_keyword in file_path.lower() for db_keyword in ['db', 'database', 'model', 'query']):
                db_operations += 1

        if db_operations == 0:
            self.add_recommendation("Consider creating dedicated database layer for optimal performance.")

        self.result.metadata['complexity_score'] = complexity_score
        self.result.metadata['db_related_files'] = db_operations

    async def _identify_optimizations(self) -> None:
        """Identify potential optimization opportunities."""
        files = self.indexer.get_files()
        dependencies = self.indexer.get_dependencies()

        optimizations = []

        # Check for excessive imports
        import_heavy_files = {}
        for dep in dependencies:
            if dep.source not in import_heavy_files:
                import_heavy_files[dep.source] = 0
            import_heavy_files[dep.source] += 1

        heavy_imports = [f for f, count in import_heavy_files.items() if count > 30]
        if heavy_imports:
            self.add_recommendation(
                f"Files {heavy_imports[:3]} have many imports. Consider lazy loading to improve startup time."
            )
            optimizations.append("lazy_loading")

        # Check for caching opportunities
        cache_files = [f for f in files.keys() if 'cache' in f.lower()]
        if not cache_files and len(files) > 50:
            self.add_recommendation(
                "Consider implementing caching for frequently accessed data to improve performance."
            )
            optimizations.append("caching")

        # Check for async operations
        async_files = [f for f in files.keys() if 'async' in f.lower()]
        if not async_files and len(files) > 20:
            self.add_recommendation(
                "Consider using async/await patterns for I/O-bound operations."
            )
            optimizations.append("async_operations")

        if optimizations:
            self.add_recommendation(f"Recommended optimizations: {', '.join(optimizations)}")

        self.result.metadata['optimization_opportunities'] = optimizations
