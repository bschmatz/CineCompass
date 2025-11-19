import { useState, useEffect, useRef } from 'react';
import type { Recommendation } from '../types';
import { api } from '../utils/api';

export function Home() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState('');
  const [ratings, setRatings] = useState<Map<number, number>>(new Map());
  const [showPoster, setShowPoster] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const ratingTimeoutRef = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map());

  useEffect(() => {
    loadRecommendations();
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        handleScroll('down');
      } else if (e.key === 'ArrowUp') {
        handleScroll('up');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, recommendations.length]);

  useEffect(() => {
    // Load more when near the end
    if (
      currentIndex >= recommendations.length - 3 &&
      !isLoadingMore &&
      hasMore
    ) {
      loadMoreRecommendations();
    }
  }, [currentIndex, recommendations.length, isLoadingMore, hasMore]);

  const loadRecommendations = async () => {
    try {
      setIsLoading(true);
      const response = await api.getRecommendations(1, 20);
      setRecommendations(response.items);
      setHasMore(response.items.length === 20);
      setPage(1);

      // Initialize ratings from userRating if available
      const initialRatings = new Map<number, number>();
      response.items.forEach(movie => {
        if (movie.userRating) {
          initialRatings.set(movie.id, movie.userRating);
        }
      });
      setRatings(initialRatings);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load recommendations');
    } finally {
      setIsLoading(false);
    }
  };

  const loadMoreRecommendations = async () => {
    if (isLoadingMore || !hasMore) return;

    try {
      setIsLoadingMore(true);
      const nextPage = page + 1;
      const response = await api.getRecommendations(nextPage, 20);
      setRecommendations((prev) => [...prev, ...response.items]);
      setHasMore(response.items.length === 20);
      setPage(nextPage);

      // Add new ratings
      response.items.forEach(movie => {
        if (movie.userRating) {
          setRatings(prev => new Map(prev).set(movie.id, movie.userRating!));
        }
      });
    } catch (err) {
      console.error('Failed to load more recommendations:', err);
    } finally {
      setIsLoadingMore(false);
    }
  };

  const handleScroll = (direction: 'up' | 'down') => {
    if (direction === 'down' && currentIndex < recommendations.length - 1) {
      setCurrentIndex(currentIndex + 1);
      containerRef.current?.children[currentIndex + 1]?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    } else if (direction === 'up' && currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      containerRef.current?.children[currentIndex - 1]?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    }
  };

  const handleRatingChange = (movieId: number, rating: number) => {
    setRatings(prev => new Map(prev).set(movieId, rating));

    // Clear existing timeout for this movie
    const existingTimeout = ratingTimeoutRef.current.get(movieId);
    if (existingTimeout) {
      clearTimeout(existingTimeout);
    }

    // Set new timeout for debounced API call
    const timeout = setTimeout(async () => {
      try {
        await api.rateMovie(movieId, rating);
        ratingTimeoutRef.current.delete(movieId);
      } catch (err) {
        console.error('Failed to save rating:', err);
      }
    }, 500);

    ratingTimeoutRef.current.set(movieId, timeout);
  };

  const handleRefresh = async () => {
    setCurrentIndex(0);
    await loadRecommendations();
    containerRef.current?.children[0]?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    });
  };

  const getPosterUrl = (posterPath: string) => {
    return `https://image.tmdb.org/t/p/original${posterPath}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading recommendations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950 px-4">
        <div className="text-center">
          <div className="bg-red-900/30 border border-red-700 text-red-400 px-6 py-4 rounded-lg mb-4">
            {error}
          </div>
          <button
            onClick={loadRecommendations}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const currentMovie = recommendations[currentIndex];

  return (
    <div className="h-screen overflow-y-scroll snap-y snap-mandatory scroll-smooth" ref={containerRef}>
      {recommendations.map((movie, index) => (
        <MovieCard
          key={movie.id}
          movie={movie}
          rating={ratings.get(movie.id)}
          onRatingChange={handleRatingChange}
          isActive={index === currentIndex}
          onPosterClick={() => setShowPoster(true)}
        />
      ))}

      {isLoadingMore && (
        <div className="h-screen flex items-center justify-center bg-gray-950 snap-start">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
            <p className="mt-4 text-gray-400">Loading more...</p>
          </div>
        </div>
      )}

      {/* Refresh button */}
      <button
        onClick={handleRefresh}
        className="fixed top-4 right-4 z-10 bg-gray-900/80 backdrop-blur-sm p-3 rounded-full hover:bg-gray-800 transition-all border border-gray-700"
        title="Refresh recommendations"
      >
        <svg
          className="w-6 h-6 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
      </button>

      {/* Poster overlay */}
      {showPoster && currentMovie && (
        <div
          className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center p-4"
          onClick={() => setShowPoster(false)}
        >
          <img
            src={getPosterUrl(currentMovie.poster_path)}
            alt={currentMovie.title}
            className="max-h-full max-w-full object-contain rounded-lg"
          />
        </div>
      )}
    </div>
  );
}

interface MovieCardProps {
  movie: Recommendation;
  rating?: number;
  onRatingChange: (movieId: number, rating: number) => void;
  isActive: boolean;
  onPosterClick: () => void;
}

function MovieCard({ movie, rating, onRatingChange, onPosterClick }: MovieCardProps) {
  const [expanded, setExpanded] = useState(false);

  const getPosterUrl = (posterPath: string) => {
    return `https://image.tmdb.org/t/p/original${posterPath}`;
  };

  const needsExpansion = movie.overview.length > 200;
  const displayOverview = expanded || !needsExpansion
    ? movie.overview
    : movie.overview.slice(0, 200) + '...';

  return (
    <div className="relative h-screen snap-start flex items-center justify-center bg-gray-950">
      {/* Background poster with gradient overlay */}
      <div className="absolute inset-0 overflow-hidden">
        <img
          src={getPosterUrl(movie.backdrop_path || movie.poster_path)}
          alt={movie.title}
          className="w-full h-full object-cover"
          onClick={onPosterClick}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/80 to-transparent"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 w-full max-w-2xl px-6 pb-20">
        {/* Title and rating badge */}
        <div className="flex items-start justify-between gap-4 mb-4">
          <h2 className="text-4xl font-bold text-white flex-1">{movie.title}</h2>
          <div className="flex items-center gap-1 bg-yellow-500/20 px-3 py-2 rounded-lg flex-shrink-0">
            <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span className="text-lg font-semibold text-yellow-500">
              {movie.vote_average.toFixed(1)}
            </span>
          </div>
        </div>

        {/* Genres */}
        <div className="flex flex-wrap gap-2 mb-4">
          {movie.genres.map((genre, idx) => (
            <span
              key={idx}
              className="px-3 py-1 bg-purple-500/30 text-purple-200 text-sm rounded-full backdrop-blur-sm"
            >
              {genre}
            </span>
          ))}
        </div>

        {/* Overview */}
        <div className="mb-6">
          <p className="text-gray-200 text-lg leading-relaxed">
            {displayOverview}
          </p>
          {needsExpansion && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-purple-400 hover:text-purple-300 mt-2 text-sm font-medium"
            >
              {expanded ? 'Show Less' : 'Show More'}
            </button>
          )}
        </div>

        {/* Cast and Director */}
        <div className="space-y-3 mb-6">
          {movie.cast && movie.cast.length > 0 && (
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <div>
                <p className="text-gray-400 text-sm">Cast</p>
                <p className="text-white">{movie.cast.slice(0, 3).join(', ')}</p>
              </div>
            </div>
          )}
          {movie.director && (
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <div>
                <p className="text-gray-400 text-sm">Director</p>
                <p className="text-white">{movie.director}</p>
              </div>
            </div>
          )}
        </div>

        {/* Rating slider */}
        <div className="bg-gray-900/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-800">
          <label className="block text-white text-lg font-semibold mb-4">
            Your Rating: {rating ? `${rating.toFixed(1)} ★` : 'Not rated'}
          </label>
          <input
            type="range"
            min="0"
            max="5"
            step="0.5"
            value={rating || 0}
            onChange={(e) => onRatingChange(movie.id, parseFloat(e.target.value))}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            style={{
              background: `linear-gradient(to right, rgb(168, 85, 247) 0%, rgb(168, 85, 247) ${((rating || 0) / 5) * 100}%, rgb(55, 65, 81) ${((rating || 0) / 5) * 100}%, rgb(55, 65, 81) 100%)`,
            }}
          />
          <div className="flex justify-between text-sm text-gray-400 mt-2">
            <span>0</span>
            <span>2.5</span>
            <span>5</span>
          </div>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 animate-bounce">
        <svg
          className="w-8 h-8 text-white/50"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 14l-7 7m0 0l-7-7m7 7V3"
          />
        </svg>
      </div>
    </div>
  );
}
