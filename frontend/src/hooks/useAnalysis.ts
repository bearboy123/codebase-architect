/**
 * Custom hook for managing analysis jobs and polling
 */
import { useState, useEffect, useCallback } from 'react';
import { apiClient, AnalysisStatus } from '../services/apiClient';

interface UseAnalysisJobResult {
  status: string;
  progress: number;
  results: any;
  loading: boolean;
  error: string | null;
  isComplete: boolean;
}

export function useAnalysisJob(jobId: string | null): UseAnalysisJobResult {
  const [status, setStatus] = useState('pending');
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(!!jobId);
  const [error, setError] = useState<string | null>(null);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!jobId) return;

    const pollJob = async () => {
      try {
        // Get status
        const statusData = await apiClient.getAnalysisStatus(jobId);
        setStatus(statusData.status);
        setProgress(statusData.progress);

        if (statusData.status === 'completed') {
          // Fetch full results
          const resultsData = await apiClient.getAnalysisResults(jobId);
          setResults(resultsData.results);
          setLoading(false);
          setIsComplete(true);
        } else if (statusData.status === 'failed') {
          setError(statusData.message);
          setLoading(false);
        } else {
          // Keep polling
          setTimeout(pollJob, 2000);
        }
      } catch (err: any) {
        setError(err.message);
        setLoading(false);
      }
    };

    pollJob();
  }, [jobId]);

  return { status, progress, results, loading, error, isComplete };
}

/**
 * Hook for detecting health color based on score
 */
export function useHealthColor(score: number): string {
  if (score >= 80) return 'text-health-excellent bg-green-50 border-green-200';
  if (score >= 60) return 'text-health-good bg-blue-50 border-blue-200';
  if (score >= 40) return 'text-health-fair bg-yellow-50 border-yellow-200';
  return 'text-health-poor bg-red-50 border-red-200';
}

/**
 * Hook for getting severity color/style
 */
export function useSeverityStyle(severity: string): { bg: string; border: string; text: string; badge: string } {
  const styles = {
    critical: {
      bg: 'bg-red-50',
      border: 'border-l-4 border-red-600',
      text: 'text-red-800',
      badge: 'badge-critical',
    },
    high: {
      bg: 'bg-orange-50',
      border: 'border-l-4 border-orange-600',
      text: 'text-orange-800',
      badge: 'badge-high',
    },
    medium: {
      bg: 'bg-yellow-50',
      border: 'border-l-4 border-yellow-600',
      text: 'text-yellow-800',
      badge: 'badge-medium',
    },
    low: {
      bg: 'bg-blue-50',
      border: 'border-l-4 border-blue-600',
      text: 'text-blue-800',
      badge: 'badge-low',
    },
  };

  return styles[severity as keyof typeof styles] || styles.low;
}
