"""
Architecture Agent - Maps services, modules, dependencies, and data flows.
"""
from typing import Dict, Set, List, Optional, Any
from collections import defaultdict
import asyncio

from semantic_kernel import Kernel

from backend.agents.base_agent import BaseAgent, AnalysisResult
from backend.analyzers.code_indexer import CodeIndexer


class ArchitectureAgent(BaseAgent):
    """
    Analyzes the overall architecture of a codebase.
    
    Maps:
    - Service boundaries and modules
    - Dependencies between components
    - Data flows
    - Architectural patterns
    """

    @property
    def agent_name(self) -> str:
        return "Architecture Agent"

    @property
    def agent_type(self) -> str:
        return "architecture"

    @property
    def description(self) -> str:
        return "Maps services, modules, dependencies, and identifies architectural patterns"

    async def analyze(self) -> AnalysisResult:
        """Perform architecture analysis."""
        self.result = AnalysisResult(
            agent_name=self.agent_name,
            agent_type=self.agent_type
        )

        try:
            # Analyze module structure
            await self._analyze_module_structure()

            # Analyze dependencies
            await self._analyze_dependencies()

            # Detect patterns
            await self._detect_patterns()

            # Identify services/boundaries
            await self._identify_services()

            self.result.status = "success"
        except Exception as e:
            self.result.status = "error"
            self.result.error_message = str(e)

        return self.result

    async def _analyze_module_structure(self) -> None:
        """Analyze the module and directory structure."""
        module_structure = self.indexer.get_module_structure()
        files = self.indexer.get_files()
        metrics = self.indexer.get_metrics()

        # Check for flat vs hierarchical structure
        num_modules = len(module_structure)
        avg_files_per_module = len(files) / num_modules if num_modules > 0 else 0

        if num_modules < 3:
            self.add_finding(
                title="Flat Module Structure",
                description=f"The codebase has only {num_modules} module(s). Consider organizing code into logical modules for better maintainability.",
                severity="low",
                location="Project root"
            )
        elif avg_files_per_module > 50:
            self.add_finding(
                title="Large Modules",
                description=f"Average files per module is {avg_files_per_module:.0f}. Large modules may indicate poor separation of concerns.",
                severity="medium",
                location="Multiple modules"
            )
        else:
            self.add_recommendation("Module structure is well-organized with good separation of concerns.")

        # Store metrics
        self.result.metadata['module_count'] = num_modules
        self.result.metadata['total_files'] = len(files)
        self.result.metadata['languages'] = metrics.languages

    async def _analyze_dependencies(self) -> None:
        """Analyze dependency patterns."""
        dependencies = self.indexer.get_dependencies()

        if not dependencies:
            self.add_recommendation("No internal dependencies detected. Ensure modules are properly connected.")
            return

        # Count dependencies by type
        dep_by_type = defaultdict(int)
        dep_by_source = defaultdict(set)

        for dep in dependencies:
            dep_by_type[dep.dependency_type] += 1
            dep_by_source[dep.source].add(dep.target)

        # Detect circular dependencies (simplified check)
        circular_deps = self._find_circular_dependencies(dependencies)
        if circular_deps:
            self.add_finding(
                title="Potential Circular Dependencies",
                description=f"Found {len(circular_deps)} potential circular dependency patterns.",
                severity="high",
                details={'circular_patterns': list(circular_deps)[:5]}
            )
        else:
            self.add_recommendation("No obvious circular dependencies detected.")

        # Check for excessive coupling
        most_imported = sorted(dep_by_source.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        if most_imported and len(most_imported[0][1]) > 20:
            self.add_finding(
                title="High Coupling Detected",
                description=f"Module '{most_imported[0][0]}' has {len(most_imported[0][1])} dependencies.",
                severity="medium",
                details={'top_coupled_modules': [m[0] for m in most_imported]}
            )

        self.result.metadata['total_dependencies'] = len(dependencies)
        self.result.metadata['unique_targets'] = len(set(d.target for d in dependencies))

    async def _detect_patterns(self) -> None:
        """Detect architectural patterns."""
        files = self.indexer.get_files()
        languages = set(f.language for f in files.values())

        patterns_detected = []

        # Microservices pattern
        if len(files) > 100 and len(self.indexer.get_module_structure()) > 10:
            patterns_detected.append("Microservices/Modular Architecture")

        # MVC/MVC-like pattern
        if any('controller' in f.path.lower() or 'view' in f.path.lower() for f in files.values()):
            patterns_detected.append("MVC/Web Framework Pattern")

        # API-first pattern
        if any('api' in f.path.lower() or f.path.endswith('_api.py') for f in files.values()):
            patterns_detected.append("API-First Architecture")

        if patterns_detected:
            self.add_recommendation(f"Detected architectural patterns: {', '.join(patterns_detected)}")
            self.result.metadata['patterns'] = patterns_detected

    async def _identify_services(self) -> None:
        """Identify service boundaries."""
        module_structure = self.indexer.get_module_structure()

        # Top-level directories are likely services
        top_level_services = [m for m in module_structure.keys() if m != 'root' and '/' not in m]

        if len(top_level_services) > 1:
            self.add_finding(
                title="Multiple Service Boundaries Identified",
                description=f"Found {len(top_level_services)} potential services/domains.",
                severity="low",
                details={'services': top_level_services}
            )
            self.result.metadata['identified_services'] = top_level_services

    def _find_circular_dependencies(self, dependencies: List) -> Set[tuple]:
        """
        Find circular dependency patterns (simplified).
        
        Args:
            dependencies: List of DependencyInfo objects
            
        Returns:
            Set of circular dependency tuples
        """
        # Build adjacency graph
        graph = defaultdict(set)
        for dep in dependencies:
            graph[dep.source].add(dep.target)

        circular = set()

        # DFS to find cycles (simplified for MVP)
        def has_cycle(node, visited, rec_stack, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack, path):
                        return True
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = tuple(path[cycle_start:] + [neighbor])
                    circular.add(cycle)
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        visited = set()
        for node in graph:
            if node not in visited:
                has_cycle(node, visited, set(), [])

        return circular
