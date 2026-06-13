/**
 * Components for displaying analysis results
 */
import { useSeverityStyle } from '../hooks/useAnalysis';

interface Finding {
  title: string;
  description: string;
  severity: string;
  location?: string;
  details?: any;
}

/**
 * Finding card component
 */
export function FindingCard({ finding }: { finding: Finding }) {
  const style = useSeverityStyle(finding.severity);

  return (
    <div className={`card ${style.bg} ${style.border} p-4 mb-3`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h4 className="font-semibold text-gray-900">{finding.title}</h4>
            <span className={`badge ${style.badge} text-xs`}>{finding.severity}</span>
          </div>
          <p className="text-sm text-gray-700 mb-2">{finding.description}</p>
          {finding.location && (
            <p className="text-xs text-gray-600">
              <strong>Location:</strong> {finding.location}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Findings list component
 */
export function FindingsList({ findings, filter }: { findings: Finding[]; filter?: string }) {
  const filtered = filter
    ? findings.filter(f => f.severity === filter)
    : findings;

  if (filtered.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No {filter ? `${filter}` : ''} findings found</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {filtered.map((finding, idx) => (
        <FindingCard key={idx} finding={finding} />
      ))}
    </div>
  );
}

/**
 * Health score display component
 */
export function HealthScore({ score }: { score: number }) {
  const getColor = (s: number) => {
    if (s >= 80) return 'text-green-600 bg-green-50 border-green-200';
    if (s >= 60) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (s >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getLabel = (s: number) => {
    if (s >= 80) return 'Excellent';
    if (s >= 60) return 'Good';
    if (s >= 40) return 'Fair';
    return 'Poor';
  };

  return (
    <div className={`card border ${getColor(score)} p-6`}>
      <p className="text-sm text-gray-600 mb-2">Overall Health Score</p>
      <div className="flex items-baseline gap-2">
        <span className="text-5xl font-bold">{score.toFixed(1)}</span>
        <span className="text-lg text-gray-600">/100 ({getLabel(score)})</span>
      </div>
      <div className="mt-4 bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${
            score >= 80 ? 'bg-green-600' : score >= 60 ? 'bg-blue-600' : score >= 40 ? 'bg-yellow-600' : 'bg-red-600'
          }`}
          style={{ width: `${score}%` }}
        ></div>
      </div>
    </div>
  );
}

/**
 * Summary statistics component
 */
export function SummaryStat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card p-4">
      <p className="text-sm text-gray-600">{label}</p>
      <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
    </div>
  );
}

/**
 * Severity summary component
 */
export function SeveritySummary({ counts }: { counts: { critical?: number; high?: number; medium?: number; low?: number } }) {
  const severities = [
    { name: 'Critical', count: counts.critical || 0, color: 'bg-red-100 text-red-800' },
    { name: 'High', count: counts.high || 0, color: 'bg-orange-100 text-orange-800' },
    { name: 'Medium', count: counts.medium || 0, color: 'bg-yellow-100 text-yellow-800' },
    { name: 'Low', count: counts.low || 0, color: 'bg-blue-100 text-blue-800' },
  ];

  return (
    <div className="card p-6">
      <h3 className="card-header">Findings by Severity</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {severities.map(s => (
          <div key={s.name} className={`p-4 rounded-lg ${s.color}`}>
            <p className="text-sm font-medium">{s.name}</p>
            <p className="text-2xl font-bold mt-2">{s.count}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Recommendations component
 */
export function RecommendationsList({ recommendations }: { recommendations: string[] }) {
  if (recommendations.length === 0) {
    return null;
  }

  return (
    <div className="card p-6">
      <h3 className="card-header">Recommendations</h3>
      <ul className="space-y-2">
        {recommendations.map((rec, idx) => (
          <li key={idx} className="flex items-start gap-3">
            <span className="text-green-600 font-bold flex-shrink-0">✓</span>
            <span className="text-gray-700">{rec}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
