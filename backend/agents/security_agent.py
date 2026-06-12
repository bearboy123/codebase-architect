"""
Security Agent - Reviews code for vulnerabilities and risky patterns.
"""
import re
from typing import Set, List
from collections import Counter

from semantic_kernel import Kernel

from backend.agents.base_agent import BaseAgent, AnalysisResult
from backend.analyzers.code_indexer import CodeIndexer


class SecurityAgent(BaseAgent):
    """
    Analyzes code for security vulnerabilities and risky patterns.
    
    Detects:
    - Hardcoded secrets/credentials
    - Unsafe library usage
    - Authentication/Authorization issues
    - Data exposure risks
    - Common vulnerabilities
    """

    # Patterns for common security issues
    SECRET_PATTERNS = {
        'api_key': r'api[_-]?key\s*[=:]\s*["\']?([a-zA-Z0-9]{20,})',
        'password': r'password\s*[=:]\s*["\']([^"\']+)["\']',
        'private_key': r'private[_-]?key\s*[=:]\s*["\']?',
        'token': r'token\s*[=:]\s*["\']([a-zA-Z0-9]{20,})',
        'aws_key': r'AKIA[0-9A-Z]{16}',
        'github_token': r'ghp_[a-zA-Z0-9]{36}',
    }

    UNSAFE_PATTERNS = {
        'sql_injection': r'execute\s*\(\s*["\']?\s*\$|execute\s*\(\s*f["\']',
        'command_injection': r'os\.system|subprocess\.call|shell=True',
        'unsafe_eval': r'eval\s*\(|exec\s*\(',
        'pickle': r'pickle\.(load|loads)',
        'xxe': r'ElementTree|minidom|sax',
    }

    UNSAFE_LIBS = {
        'requests': 'Missing SSL verification possible - ensure verify=True',
        'pickle': 'Unsafe deserialization - consider using JSON',
        'eval': 'Arbitrary code execution risk',
        'exec': 'Arbitrary code execution risk',
    }

    @property
    def agent_name(self) -> str:
        return "Security Agent"

    @property
    def agent_type(self) -> str:
        return "security"

    @property
    def description(self) -> str:
        return "Reviews code for security vulnerabilities and risky patterns"

    async def analyze(self) -> AnalysisResult:
        """Perform security analysis."""
        self.result = AnalysisResult(
            agent_name=self.agent_name,
            agent_type=self.agent_type
        )

        try:
            # Scan for secrets
            await self._scan_for_secrets()

            # Scan for unsafe patterns
            await self._scan_for_unsafe_patterns()

            # Check dependencies
            await self._check_unsafe_dependencies()

            # Authentication analysis
            await self._analyze_auth_patterns()

            self.result.status = "success"
        except Exception as e:
            self.result.status = "error"
            self.result.error_message = str(e)

        return self.result

    async def _scan_for_secrets(self) -> None:
        """Scan files for hardcoded secrets."""
        files = self.indexer.get_files()
        secrets_found = []

        # Focus on code files
        for file_path, file_info in files.items():
            if file_info.language not in ['python', 'javascript', 'typescript', 'java', 'go']:
                continue

            try:
                full_path = self.indexer.repo_path / file_path
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern_name, pattern in self.SECRET_PATTERNS.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        secrets_found.append((pattern_name, file_path))
                        self.add_finding(
                            title=f"Potential {pattern_name.replace('_', ' ').title()} Hardcoded",
                            description=f"Possible hardcoded {pattern_name} detected in {file_path}. Move to environment variables.",
                            severity="critical",
                            location=file_path,
                            details={'pattern': pattern_name}
                        )
                        break
            except Exception:
                continue

        if not secrets_found:
            self.add_recommendation("No obvious hardcoded secrets detected.")

        self.result.metadata['secrets_scanned'] = len(secrets_found)

    async def _scan_for_unsafe_patterns(self) -> None:
        """Scan for unsafe coding patterns."""
        files = self.indexer.get_files()
        unsafe_patterns_found = []

        for file_path, file_info in files.items():
            if file_info.language not in ['python', 'javascript', 'typescript']:
                continue

            try:
                full_path = self.indexer.repo_path / file_path
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern_name, pattern in self.UNSAFE_PATTERNS.items():
                    matches = len(re.findall(pattern, content, re.IGNORECASE))
                    if matches > 0:
                        unsafe_patterns_found.append(pattern_name)
                        severity = "high" if pattern_name in ['sql_injection', 'command_injection'] else "medium"
                        self.add_finding(
                            title=f"Unsafe Pattern: {pattern_name.replace('_', ' ').title()}",
                            description=f"Detected {matches} occurrence(s) of {pattern_name}.",
                            severity=severity,
                            location=file_path,
                            details={'pattern': pattern_name, 'count': matches}
                        )
            except Exception:
                continue

        if not unsafe_patterns_found:
            self.add_recommendation("No obvious unsafe patterns detected in code.")

        self.result.metadata['unsafe_patterns'] = list(set(unsafe_patterns_found))

    async def _check_unsafe_dependencies(self) -> None:
        """Check for unsafe/risky dependencies."""
        files = self.indexer.get_files()
        unsafe_libs_found = []

        # Look for unsafe library usage
        for file_path, file_info in files.items():
            if file_info.language not in ['python', 'javascript', 'typescript']:
                continue

            try:
                full_path = self.indexer.repo_path / file_path
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for lib, risk in self.UNSAFE_LIBS.items():
                    if re.search(rf'\b{lib}\b', content, re.IGNORECASE):
                        unsafe_libs_found.append(lib)
                        self.add_finding(
                            title=f"Risky Library: {lib}",
                            description=f"{risk}. Review usage in {file_path}.",
                            severity="medium" if lib != 'eval' else "high",
                            location=file_path
                        )
            except Exception:
                continue

        if not unsafe_libs_found:
            self.add_recommendation("No obviously risky libraries detected.")

        self.result.metadata['unsafe_libraries'] = list(set(unsafe_libs_found))

    async def _analyze_auth_patterns(self) -> None:
        """Analyze authentication and authorization patterns."""
        files = self.indexer.get_files()
        auth_files = []

        for file_path in files.keys():
            if any(auth_keyword in file_path.lower() for auth_keyword in ['auth', 'security', 'permission']):
                auth_files.append(file_path)

        if not auth_files:
            self.add_finding(
                title="No Dedicated Auth Module Found",
                description="Consider creating dedicated modules for authentication and authorization.",
                severity="low"
            )
        else:
            self.add_recommendation(f"Found {len(auth_files)} authentication-related files. Ensure they follow security best practices.")

        # Check for HTTPS/TLS in API files
        api_files = [f for f in files.keys() if 'api' in f.lower()]
        for file_path in api_files:
            try:
                full_path = self.indexer.repo_path / file_path
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                if re.search(r'http://', content) and not re.search(r'https://', content):
                    self.add_finding(
                        title="Unencrypted HTTP Communication",
                        description=f"File {file_path} may use unencrypted HTTP. Use HTTPS instead.",
                        severity="high",
                        location=file_path
                    )
            except Exception:
                continue

        self.result.metadata['auth_files_found'] = len(auth_files)
