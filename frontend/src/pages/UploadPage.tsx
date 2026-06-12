/**
 * Upload/Repository input page
 */
import { useState } from 'react';
import { apiClient } from '../services/apiClient';
import { ErrorMessage, SuccessMessage } from '../components/Layout';

interface UploadPageProps {
  onAnalysisStart: (jobId: string) => void;
}

export function UploadPage({ onAnalysisStart }: UploadPageProps) {
  const [activeTab, setActiveTab] = useState<'url' | 'upload'>('url');
  const [repoUrl, setRepoUrl] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!repoUrl.trim()) {
      setError('Please enter a repository URL');
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.startAnalysis({ repo_url: repoUrl });
      setSuccess('Analysis started! Redirecting...');
      setTimeout(() => onAnalysisStart(response.job_id), 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to start analysis');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.uploadRepository(file);
      setSuccess('Analysis started! Redirecting...');
      setTimeout(() => onAnalysisStart(response.job_id), 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to upload and analyze repository');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
      <div className="max-w-2xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Analyze Your Codebase
          </h2>
          <p className="text-xl text-gray-600">
            Upload a repository or provide a Git URL to get started with intelligent code analysis
          </p>
        </div>

        {error && (
          <ErrorMessage message={error} onDismiss={() => setError('')} />
        )}
        {success && (
          <SuccessMessage message={success} onDismiss={() => setSuccess('')} />
        )}

        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Tabs */}
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('url')}
              className={`flex-1 py-4 px-6 font-semibold text-center transition-colors ${
                activeTab === 'url'
                  ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Git Repository URL
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex-1 py-4 px-6 font-semibold text-center transition-colors ${
                activeTab === 'upload'
                  ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Upload Repository
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-8">
            {activeTab === 'url' ? (
              <form onSubmit={handleUrlSubmit}>
                <div className="mb-6">
                  <label htmlFor="repo-url" className="block text-sm font-semibold text-gray-700 mb-3">
                    Repository URL
                  </label>
                  <input
                    id="repo-url"
                    type="url"
                    placeholder="https://github.com/username/repo.git"
                    value={repoUrl}
                    onChange={e => setRepoUrl(e.target.value)}
                    disabled={loading}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                  />
                  <p className="text-sm text-gray-500 mt-2">
                    Supports public Git repositories (GitHub, GitLab, Gitea, etc.)
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary w-full"
                >
                  {loading ? 'Starting Analysis...' : 'Analyze Repository'}
                </button>
              </form>
            ) : (
              <form onSubmit={handleFileUpload}>
                <div className="mb-6">
                  <label
                    htmlFor="file-upload"
                    className="block border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors"
                  >
                    <svg
                      className="mx-auto h-12 w-12 text-gray-400 mb-3"
                      stroke="currentColor"
                      fill="none"
                      viewBox="0 0 48 48"
                    >
                      <path
                        d="M28 8H12a4 4 0 00-4 4v20a4 4 0 004 4h24a4 4 0 004-4V20m-6-10l-6-6m6 6v12m0 0H12v-4"
                        strokeWidth={2}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    <p className="text-lg font-semibold text-gray-700">
                      {file ? file.name : 'Click to upload or drag and drop'}
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      ZIP file of your repository (max 100MB)
                    </p>
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    accept=".zip,.tar,.tar.gz"
                    onChange={e => setFile(e.target.files?.[0] || null)}
                    disabled={loading}
                    className="hidden"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading || !file}
                  className="btn-primary w-full"
                >
                  {loading ? 'Uploading & Analyzing...' : 'Upload & Analyze'}
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Features */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg p-6 shadow">
            <div className="text-3xl mb-3">🏗️</div>
            <h3 className="font-semibold text-gray-900 mb-2">Architecture</h3>
            <p className="text-gray-600 text-sm">Maps services, modules, and dependencies</p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow">
            <div className="text-3xl mb-3">🔒</div>
            <h3 className="font-semibold text-gray-900 mb-2">Security</h3>
            <p className="text-gray-600 text-sm">Identifies vulnerabilities and risky patterns</p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow">
            <div className="text-3xl mb-3">⚡</div>
            <h3 className="font-semibold text-gray-900 mb-2">Performance</h3>
            <p className="text-gray-600 text-sm">Detects inefficiencies and bottlenecks</p>
          </div>
        </div>
      </div>
    </div>
  );
}
