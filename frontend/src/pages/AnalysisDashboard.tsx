/**
 * Analysis results dashboard page
 */
import { useState } from 'react';
import { useAnalysisJob } from '../hooks/useAnalysis';
import { ErrorMessage, ProgressBar } from '../components/Layout';
import {
  HealthScore,
  SeveritySummary,
  FindingsList,
  RecommendationsList,
  SummaryStat,
} from '../components/Results';

interface AnalysisDashboardProps {
  jobId: string;
  onBack: () => void;
}

export function AnalysisDashboard({ jobId, onBack }: AnalysisDashboardProps) {
  const { status, progress, results, loading, error, isComplete } = useAnalysisJob(jobId);
  const [activeTab, setActiveTab] = useState<'overview' | 'architecture' | 'security' | 'performance'>('overview');
  const [severityFilter, setSeverityFilter] = useState<string | undefined>();

  if (loading && !isComplete) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-6">
          <div className="bg-white rounded-lg shadow p-8">
            <h2 className="text-2xl font-bold mb-8 text-gray-900">Analyzing Your Codebase</h2>

            <div className="mb-8">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-gray-700">Overall Progress</p>
                <p className="text-sm text-gray-600">{progress}%</p>
              </div>
              <ProgressBar progress={progress} />
            </div>

            {status === 'running' && (
              <div className="mb-8">
                <p className="text-gray-600 mb-4">Agents running:</p>
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                    <span className="text-gray-700">Architecture Agent</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                    <span className="text-gray-700">Security Agent</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                    <span className="text-gray-700">Performance Agent</span>
                  </div>
                </div>
              </div>
            )}

            <button
              onClick={onBack}
              className="btn-secondary"
            >
              Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-6">
          <ErrorMessage message={error} />
          <button onClick={onBack} className="btn-secondary">
            Back
          </button>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-6">
          <p className="text-gray-600">No results available</p>
          <button onClick={onBack} className="btn-secondary mt-4">
            Back
          </button>
        </div>
      </div>
    );
  }

  const summary = results.summary || {};
  const findings = results.findings || [];
  const recommendations = results.recommendations || [];
  const agents = results.agents || {};
  const metrics = results.indexed_metrics || {};

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-6">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={onBack}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center gap-2"
          >
            ← Back
          </button>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Analysis Results</h1>
          <p className="text-gray-600">
            Analysis completed in {results.execution_time_ms?.toFixed(0)}ms
          </p>
        </div>

        {/* Health Score */}
        <div className="mb-8">
          <HealthScore score={summary.health_score || 0} />
        </div>

        {/* Summary Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <SummaryStat label="Total Findings" value={summary.total_findings || 0} />
          <SummaryStat label="Critical Issues" value={summary.findings_by_severity?.critical || 0} />
          <SummaryStat label="Files Analyzed" value={metrics.total_files || 0} />
          <SummaryStat label="Total Lines" value={metrics.total_lines?.toLocaleString() || 0} />
        </div>

        {/* Severity Summary */}
        {findings.length > 0 && (
          <div className="mb-8">
            <SeveritySummary counts={summary.findings_by_severity || {}} />
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow overflow-hidden mb-8">
          <div className="flex border-b border-gray-200">
            {['overview', 'architecture', 'security', 'performance'].map(tab => (
              <button
                key={tab}
                onClick={() => {
                  setActiveTab(tab as any);
                  setSeverityFilter(undefined);
                }}
                className={`flex-1 py-4 px-6 font-semibold text-center transition-colors capitalize ${
                  activeTab === tab
                    ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="p-8">
            {activeTab === 'overview' && (
              <div>
                <h2 className="text-2xl font-bold mb-6 text-gray-900">Overview</h2>
                <div className="mb-8">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">Agents Executed</h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Object.entries(agents).map(([key, agent]: [string, any]) => (
                      <div key={key} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <p className="font-semibold text-gray-900 capitalize">{key} Agent</p>
                        <p className="text-sm text-gray-600 mt-2">
                          Status: <span className="font-medium capitalize">{agent.status}</span>
                        </p>
                        <p className="text-sm text-gray-600">
                          Findings: <span className="font-medium">{agent.findings_count}</span>
                        </p>
                        <p className="text-sm text-gray-600">
                          Time: <span className="font-medium">{agent.execution_time_ms?.toFixed(0)}ms</span>
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {recommendations.length > 0 && (
                  <RecommendationsList recommendations={recommendations} />
                )}
              </div>
            )}

            {activeTab === 'architecture' && (
              <div>
                <h2 className="text-2xl font-bold mb-6 text-gray-900">Architecture Findings</h2>
                <div className="mb-6">
                  <label className="text-sm font-medium text-gray-700 block mb-2">
                    Filter by Severity:
                  </label>
                  <div className="flex gap-2">
                    {[undefined, 'critical', 'high', 'medium', 'low'].map(severity => (
                      <button
                        key={severity}
                        onClick={() => setSeverityFilter(severity)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          severityFilter === severity
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                      >
                        {severity ? severity.charAt(0).toUpperCase() + severity.slice(1) : 'All'}
                      </button>
                    ))}
                  </div>
                </div>
                <FindingsList
                  findings={findings.filter((f: any) => f.severity !== 'critical' && f.severity !== 'high')}
                  filter={severityFilter}
                />
              </div>
            )}

            {activeTab === 'security' && (
              <div>
                <h2 className="text-2xl font-bold mb-6 text-gray-900">Security Findings</h2>
                <div className="mb-6">
                  <label className="text-sm font-medium text-gray-700 block mb-2">
                    Filter by Severity:
                  </label>
                  <div className="flex gap-2">
                    {[undefined, 'critical', 'high', 'medium', 'low'].map(severity => (
                      <button
                        key={severity}
                        onClick={() => setSeverityFilter(severity)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          severityFilter === severity
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                      >
                        {severity ? severity.charAt(0).toUpperCase() + severity.slice(1) : 'All'}
                      </button>
                    ))}
                  </div>
                </div>
                <FindingsList findings={findings} filter={severityFilter} />
              </div>
            )}

            {activeTab === 'performance' && (
              <div>
                <h2 className="text-2xl font-bold mb-6 text-gray-900">Performance Findings</h2>
                <div className="mb-6">
                  <label className="text-sm font-medium text-gray-700 block mb-2">
                    Filter by Severity:
                  </label>
                  <div className="flex gap-2">
                    {[undefined, 'critical', 'high', 'medium', 'low'].map(severity => (
                      <button
                        key={severity}
                        onClick={() => setSeverityFilter(severity)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          severityFilter === severity
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                      >
                        {severity ? severity.charAt(0).toUpperCase() + severity.slice(1) : 'All'}
                      </button>
                    ))}
                  </div>
                </div>
                <FindingsList findings={findings} filter={severityFilter} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
