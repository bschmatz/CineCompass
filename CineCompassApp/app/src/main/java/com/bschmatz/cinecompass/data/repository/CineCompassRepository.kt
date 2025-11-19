package com.bschmatz.cinecompass.data.repository

import com.bschmatz.cinecompass.data.api.CineCompassApi
import com.bschmatz.cinecompass.data.models.BatchRatingRequest
import com.bschmatz.cinecompass.data.models.BatchRatingResponse
import com.bschmatz.cinecompass.data.models.MovieRating
import com.bschmatz.cinecompass.data.models.PopularMovie
import com.bschmatz.cinecompass.data.models.RecommendationResponse
import javax.inject.Inject

class CineCompassRepository @Inject constructor(
    private val api: CineCompassApi
) {
    suspend fun getRecommendations(
        sessionId: String,
        page: Int,
        pageSize: Int,
        lastSyncTime: String? = null
    ): Result<RecommendationResponse> =
        try {
            Result.success(
                api.getRecommendations(
                    page = page,
                    pageSize = pageSize,
                    lastSyncTime = lastSyncTime,
                    sessionId = sessionId
                )
            )
        } catch (e: Exception) {
            Result.failure(e)
        }

    suspend fun submitRating(sessionId: String, movieId: Int, rating: Double): Result<Unit> =
        try {
            Result.success(
                api.submitRating(
                    MovieRating(movieId = movieId, rating = rating),
                    sessionId = sessionId
                )
            )
        } catch (e: Exception) {
            Result.failure(e)
        }

    suspend fun getPopularMovies(limit: Int = 10): Result<List<PopularMovie>> =
        try {
            Result.success(api.getPopularMovies(limit))
        } catch (e: Exception) {
            Result.failure(e)
        }

    suspend fun submitBatchRatings(
        sessionId: String,
        ratings: List<MovieRating>
    ): Result<BatchRatingResponse> =
        try {
            val request = BatchRatingRequest(ratings)
            Result.success(api.submitBatchRatings(request, sessionId))
        } catch (e: Exception) {
            Result.failure(e)
        }

    suspend fun refreshSessions(sessionId: String): Result<Unit> =
        try {
            Result.success(api.refreshSession(sessionId))
        } catch (e: Exception) {
            Result.failure(e)
        }

    suspend fun isOnboarded(sessionId: String): Result<Boolean> =
        try {
            Result.success(api.isOnboarded(sessionId))
        } catch (e: Exception) {
            Result.failure(e)
        }
}