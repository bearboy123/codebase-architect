/**
 * API client service for backend communication
 */
import axios, { AxiosInstance } from 'axios';

interface AnalysisRequest {
  repo_url?: string;
  repo_path?: string;
}

interface AnalysisResponse {
  job_id: string;
  status: string;
  results?: any;
}

interface AnalysisStatus {
  job_id: string;
  status: string;
  progress: number;
  message: string;
}

class APIClient {
  private client: AxiosInstance;

  constructor(baseURL: string = '/api') {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Start a new analysis job
   */
  async startAnalysis(request: AnalysisRequest): Promise<AnalysisResponse> {
    const response = await this.client.post<AnalysisResponse>('/analyze', request);
    return response.data;
  }

  /**
   * Get analysis results
   */
  async getAnalysisResults(jobId: string): Promise<any> {
    const response = await this.client.get(`/analysis/${jobId}`);
    return response.data;
  }

  /**
   * Get analysis status
   */
  async getAnalysisStatus(jobId: string): Promise<AnalysisStatus> {
    const response = await this.client.get<AnalysisStatus>(`/analysis/${jobId}/status`);
    return response.data;
  }

  /**
   * Upload and analyze a repository
   */
  async uploadRepository(file: File): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<AnalysisResponse>(
      '/analyze/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  /**
   * Get system metrics
   */
  async getMetrics(): Promise<any> {
    const response = await this.client.get('/metrics');
    return response.data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const apiClient = new APIClient();
export type { AnalysisRequest, AnalysisResponse, AnalysisStatus };
