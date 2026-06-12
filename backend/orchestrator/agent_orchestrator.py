"""
Agent Orchestrator - Coordinates and manages multiple agent analyses.
"""
import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from datetime import datetime

from semantic_kernel import Kernel

from backend.analyzers.code_indexer import CodeIndexer
from backend.agents.architecture_agent import ArchitectureAgent
from backend.agents.security_agent import SecurityAgent
from backend.agents.performance_agent import PerformanceAgent
from backend.agents.base_agent import AnalysisResult


class AgentOrchestrator:
    """
    Orchestrates multiple specialized agents to analyze a codebase.
    
    Responsibilities:
    - Coordinate agent execution
    - Share findings between agents
    - Consolidate results
    - Generate unified reports
    """

    def __init__(self, kernel: Kernel, code_indexer: CodeIndexer):
        """
        Initialize the orchestrator.
        
        Args:
            kernel: Semantic Kernel instance
            code_indexer: Indexed codebase information
        """
        self.kernel = kernel
        self.indexer = code_indexer
        self.agents = self._initialize_agents()
        self.results: Dict[str, AnalysisResult] = {}
        self.execution_start: Optional[datetime] = None
        self.execution_end: Optional[datetime] = None

    def _initialize_agents(self) -> Dict[str, Any]:
        """Create and return all analysis agents."""
        return {
            'architecture': ArchitectureAgent(self.kernel, self.indexer),
            'security': SecurityAgent(self.kernel, self.indexer),
            'performance': PerformanceAgent(self.kernel, self.indexer),
        }

    async def analyze(self) -> Dict[str, Any]:
        """
        Run all agents and produce consolidated analysis.
        
        Returns:
            Dict containing all agent results and consolidated report
        """
        self.execution_start = datetime.now()

        try:
            # Run all agents in parallel
            tasks = []
            for agent_type, agent in self.agents.items():
                task = self._execute_agent(agent_type, agent)
                tasks.append(task)

            # Wait for all agents to complete
            await asyncio.gather(*tasks)

            # Generate consolidated report
            report = self._generate_consolidated_report()

            return report

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'execution_time_ms': self._get_execution_time()
            }
        finally:
            self.execution_end = datetime.now()

    async def _execute_agent(self, agent_type: str, agent) -> None:
        """
        Execute a single agent with error handling.
        
        Args:
            agent_type: Type of agent (key in agents dict)
            agent: Agent instance to execute
        """
        try:
            result = await agent._execute_with_timing()
            self.results[agent_type] = result
        except Exception as e:
            # Store error result
            error_result = AnalysisResult(
                agent_name=agent.agent_name,
                agent_type=agent.agent_type,
                status="error",
                error_message=str(e)
            )
            self.results[agent_type] = error_result

    def _generate_consolidated_report(self) -> Dict[str, Any]:
        """
        Generate a consolidated report from all agent results.
        
        Returns:
            Consolidated analysis report
        """
        # Aggregate findings by severity
        all_findings = []
        all_recommendations = set()

        for result in self.results.values():
            if result and result.findings:
                all_findings.extend(result.findings)
            if result and result.recommendations:
                all_recommendations.update(result.recommendations)

        # Sort findings by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_findings.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))

        # Count by severity
        severity_counts = {}
        for finding in all_findings:
            severity = finding.get('severity', 'low')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Calculate overall health score
        health_score = self._calculate_health_score(severity_counts, len(all_findings))

        report = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'execution_time_ms': self._get_execution_time(),
            'indexed_metrics': asdict(self.indexer.get_metrics()),
            'summary': {
                'total_findings': len(all_findings),
                'findings_by_severity': severity_counts,
                'health_score': health_score,
                'total_recommendations': len(all_recommendations),
                'agents_executed': len(self.results)
            },
            'agents': self._serialize_agent_results(),
            'findings': all_findings,
            'recommendations': sorted(list(all_recommendations)),
        }

        return report

    def _serialize_agent_results(self) -> Dict[str, Any]:
        """Serialize agent results for reporting."""
        serialized = {}

        for agent_type, result in self.results.items():
            if result:
                serialized[agent_type] = {
                    'agent_name': result.agent_name,
                    'status': result.status,
                    'execution_time_ms': result.execution_time_ms,
                    'findings_count': len(result.findings),
                    'recommendations_count': len(result.recommendations),
                    'error': result.error_message,
                    'metadata': result.metadata,
                }

        return serialized

    def _calculate_health_score(self, severity_counts: Dict[str, int], total_findings: int) -> float:
        """
        Calculate overall code health score (0-100).
        
        Args:
            severity_counts: Count of findings by severity
            total_findings: Total number of findings
            
        Returns:
            Health score from 0 to 100
        """
        if total_findings == 0:
            return 100.0

        # Weighted scoring
        critical_weight = 100
        high_weight = 50
        medium_weight = 20
        low_weight = 5

        penalty = (
            severity_counts.get('critical', 0) * critical_weight +
            severity_counts.get('high', 0) * high_weight +
            severity_counts.get('medium', 0) * medium_weight +
            severity_counts.get('low', 0) * low_weight
        )

        # Normalize to 0-100 scale
        health_score = max(0, 100 - (penalty / (critical_weight * 10)))
        return round(health_score, 2)

    def _get_execution_time(self) -> float:
        """Get total execution time in milliseconds."""
        if self.execution_start and self.execution_end:
            duration = (self.execution_end - self.execution_start).total_seconds()
            return round(duration * 1000, 2)
        return 0.0

    def get_result(self, agent_type: str) -> Optional[AnalysisResult]:
        """Get result from a specific agent."""
        return self.results.get(agent_type)

    def get_all_findings(self) -> List[Dict[str, Any]]:
        """Get all findings from all agents."""
        findings = []
        for result in self.results.values():
            if result and result.findings:
                findings.extend(result.findings)
        return findings

    def get_critical_findings(self) -> List[Dict[str, Any]]:
        """Get only critical severity findings."""
        return [f for f in self.get_all_findings() if f.get('severity') == 'critical']

    def get_findings_by_agent(self, agent_type: str) -> List[Dict[str, Any]]:
        """Get findings from a specific agent."""
        result = self.results.get(agent_type)
        return result.findings if result else []

    def export_report(self, output_path: str) -> str:
        """
        Export consolidated report to JSON file.
        
        Args:
            output_path: Path to save the report
            
        Returns:
            Path to saved report
        """
        if not self.results:
            raise ValueError("No analysis results to export. Run analyze() first.")

        report = self._generate_consolidated_report()

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return output_path
