"""
Base agent class and common interface for all specialized agents.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from semantic_kernel import Kernel

from backend.analyzers.code_indexer import CodeIndexer, CodeMetrics


@dataclass
class AnalysisResult:
    """Result from an agent's analysis."""
    agent_name: str
    agent_type: str
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    severity_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    status: str = "success"  # success, partial, error
    error_message: Optional[str] = None


class BaseAgent(ABC):
    """
    Abstract base class for all analysis agents.
    
    Each agent analyzes a specific aspect of a codebase and produces findings
    and recommendations.
    """

    def __init__(self, kernel: Kernel, code_indexer: CodeIndexer):
        """
        Initialize the agent.
        
        Args:
            kernel: Semantic Kernel instance for LLM interaction
            code_indexer: CodeIndexer instance with repository analysis
        """
        self.kernel = kernel
        self.indexer = code_indexer
        self.result: Optional[AnalysisResult] = None
        self.execution_start: Optional[datetime] = None

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Name of the agent."""
        pass

    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Type of agent (e.g., 'architecture', 'security', 'performance')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this agent analyzes."""
        pass

    @abstractmethod
    async def analyze(self) -> AnalysisResult:
        """
        Perform analysis on the indexed codebase.
        
        Returns:
            AnalysisResult: Findings and recommendations
        """
        pass

    async def _execute_with_timing(self):
        """Execute analysis and track execution time."""
        self.execution_start = datetime.now()
        try:
            self.result = await self.analyze()
            execution_time = (datetime.now() - self.execution_start).total_seconds() * 1000
            self.result.execution_time_ms = execution_time
            return self.result
        except Exception as e:
            execution_time = (datetime.now() - self.execution_start).total_seconds() * 1000
            self.result = AnalysisResult(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                status="error",
                error_message=str(e),
                execution_time_ms=execution_time
            )
            return self.result

    def get_indexed_data(self) -> Dict[str, Any]:
        """Get indexed repository data."""
        return self.indexer.to_dict()

    def get_metrics(self) -> CodeMetrics:
        """Get code metrics from indexer."""
        return self.indexer.get_metrics()

    def get_files(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Get indexed files."""
        files = self.indexer.get_files(language)
        return {k: {
            'path': v.path,
            'language': v.language,
            'lines': v.lines_of_code,
            'size': v.size_bytes,
            'is_test': v.has_tests
        } for k, v in files.items()}

    def get_dependencies(self) -> List[Dict[str, str]]:
        """Get dependency information."""
        deps = self.indexer.get_dependencies()
        return [
            {'source': d.source, 'target': d.target, 'type': d.dependency_type}
            for d in deps
        ]

    def add_finding(self, title: str, description: str, severity: str = "medium",
                   location: Optional[str] = None, details: Optional[Dict] = None) -> None:
        """
        Add a finding to the current analysis result.
        
        Args:
            title: Title of the finding
            description: Detailed description
            severity: Severity level (critical, high, medium, low)
            location: File/code location
            details: Additional details dict
        """
        if self.result is None:
            self.result = AnalysisResult(
                agent_name=self.agent_name,
                agent_type=self.agent_type
            )

        severity_score = {
            'critical': 1.0,
            'high': 0.75,
            'medium': 0.5,
            'low': 0.25
        }.get(severity, 0.5)

        finding = {
            'title': title,
            'description': description,
            'severity': severity,
            'location': location,
            'details': details or {}
        }
        self.result.findings.append(finding)
        self.result.severity_scores[title] = severity_score

    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation to the result."""
        if self.result is None:
            self.result = AnalysisResult(
                agent_name=self.agent_name,
                agent_type=self.agent_type
            )
        self.result.recommendations.append(recommendation)

    def get_result(self) -> Optional[AnalysisResult]:
        """Get the current analysis result."""
        return self.result
