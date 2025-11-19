export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface Movie {
  id: number;
  title: string;
  overview: string;
  genres: string[];
  poster_path: string;
  vote_average: number;
  popularity: number;
}

export interface Recommendation extends Movie {
  similarity_score?: number;
  cast: string[];
  director: string;
  backdrop_path: string;
  userRating?: number;
}

export interface RecommendationsResponse {
  items: Recommendation[];
  total: number;
  page: number;
  page_size: number;
  needs_sync?: boolean;
  new_ratings?: Array<{ movie_id: number; rating: number }>;
}

export interface MovieRating {
  movie_id: number;
  rating: number;
}

export interface BatchRatingResponse {
  status: string;
  message: string;
}
