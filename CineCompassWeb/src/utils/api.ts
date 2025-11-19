import type {
  Movie,
  RecommendationsResponse,
  MovieRating,
  BatchRatingResponse,
} from '../types';
import { getSessionId } from './auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const sessionId = getSessionId();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-Session-ID': sessionId,
      ...(options.headers as Record<string, string>),
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getRecommendations(
    page: number = 1,
    pageSize: number = 20,
    lastSyncTime?: string
  ): Promise<RecommendationsResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    if (lastSyncTime) {
      params.append('last_sync_time', lastSyncTime);
    }

    return this.request<RecommendationsResponse>(
      `/recommendations?${params.toString()}`
    );
  }

  async rateMovie(movieId: number, rating: number): Promise<void> {
    await this.request('/ratings', {
      method: 'POST',
      body: JSON.stringify({ movie_id: movieId, rating }),
    });
  }

  async getPopularMovies(limit: number = 10): Promise<Movie[]> {
    return this.request<Movie[]>(`/movies/popular?limit=${limit}`);
  }

  async batchRateMovies(ratings: MovieRating[]): Promise<BatchRatingResponse> {
    return this.request<BatchRatingResponse>('/ratings/batch', {
      method: 'POST',
      body: JSON.stringify({ ratings }),
    });
  }

  async refreshSession(): Promise<void> {
    await this.request('/refresh-session', {
      method: 'POST',
    });
  }

  async isOnboarded(): Promise<boolean> {
    return this.request<boolean>('/is-onboarded');
  }

  async initSession(): Promise<{ session_id: string; has_finished_onboarding: boolean }> {
    return this.request('/init-session', {
      method: 'POST',
    });
  }
}

export const api = new ApiClient();
