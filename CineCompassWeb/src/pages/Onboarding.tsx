import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';
import type { Movie, MovieRating } from '../types';

const RATING_VALUES = [2, 4, 6, 8, 10];
const MIN_RATINGS = 5;

export function Onboarding() {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [ratings, setRatings] = useState<Map<number, number>>(new Map());
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadPopularMovies();
  }, []);

  const loadPopularMovies = async () => {
    try {
      const popularMovies = await api.getPopularMovies(10);
      setMovies(popularMovies);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load movies');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRating = (movieId: number, rating: number) => {
    const newRatings = new Map(ratings);
    if (newRatings.get(movieId) === rating) {
      newRatings.delete(movieId);
    } else {
      newRatings.set(movieId, rating);
    }
    setRatings(newRatings);
  };

  const handleSubmit = async () => {
    if (ratings.size < MIN_RATINGS) return;

    setIsSubmitting(true);
    setError('');

    try {
      const ratingArray: MovieRating[] = Array.from(ratings.entries()).map(
        ([movie_id, rating]) => ({ movie_id, rating })
      );
      await api.batchRateMovies(ratingArray);
      navigate('/home');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit ratings');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getPosterUrl = (posterPath: string) => {
    return `https://image.tmdb.org/t/p/w500${posterPath}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading movies...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-600 text-transparent bg-clip-text">
            Welcome to CineCompass
          </h1>
          <p className="text-gray-400 text-lg">
            Rate at least {MIN_RATINGS} movies to get personalized recommendations
          </p>
          <p className="text-purple-400 font-semibold mt-2">
            {ratings.size} / {MIN_RATINGS} movies rated
          </p>
        </div>

        {error && (
          <div className="bg-red-900/30 border border-red-700 text-red-400 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <div className="space-y-4 mb-8">
          {movies.map((movie) => (
            <div
              key={movie.id}
              className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden hover:border-purple-500/50 transition-all"
            >
              <div className="flex gap-4 p-4">
                <img
                  src={getPosterUrl(movie.poster_path)}
                  alt={movie.title}
                  className="w-24 h-36 object-cover rounded-lg flex-shrink-0"
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <h3 className="text-xl font-semibold text-white line-clamp-2">
                      {movie.title}
                    </h3>
                    <div className="flex items-center gap-1 bg-yellow-500/20 px-2 py-1 rounded-lg flex-shrink-0">
                      <svg
                        className="w-4 h-4 text-yellow-500"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                      <span className="text-sm font-medium text-yellow-500">
                        {movie.vote_average.toFixed(1)}
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {movie.genres.map((genre, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded-full"
                      >
                        {genre}
                      </span>
                    ))}
                  </div>
                  <p className="text-gray-400 text-sm line-clamp-3 mb-4">
                    {movie.overview}
                  </p>
                  <div className="flex items-center gap-2">
                    {RATING_VALUES.map((value) => {
                      const isSelected = ratings.get(movie.id) === value;
                      return (
                        <button
                          key={value}
                          onClick={() => handleRating(movie.id, value)}
                          className={`p-2 rounded-lg transition-all ${
                            isSelected
                              ? 'text-red-500 scale-110'
                              : 'text-gray-600 hover:text-red-400 hover:scale-105'
                          }`}
                        >
                          <svg
                            className="w-8 h-8"
                            fill={isSelected ? 'currentColor' : 'none'}
                            stroke="currentColor"
                            strokeWidth="2"
                            viewBox="0 0 24 24"
                          >
                            <path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                          </svg>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="sticky bottom-0 bg-gray-950/95 backdrop-blur-sm py-4 border-t border-gray-800">
          <button
            onClick={handleSubmit}
            disabled={ratings.size < MIN_RATINGS || isSubmitting}
            className="w-full bg-gradient-to-r from-purple-500 to-pink-600 text-white py-4 rounded-xl font-semibold hover:from-purple-600 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <span className="flex items-center justify-center">
                <svg
                  className="animate-spin h-5 w-5 mr-2"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Submitting...
              </span>
            ) : (
              `Continue (${ratings.size}/${MIN_RATINGS})`
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
