package com.bschmatz.cinecompass.data.repository

import com.bschmatz.cinecompass.data.api.CineCompassApi
import com.bschmatz.cinecompass.data.models.BatchRatingRequest
import com.bschmatz.cinecompass.data.models.BatchRatingResponse
import com.bschmatz.cinecompass.data.models.LoginRequest
import com.bschmatz.cinecompass.data.models.MovieRating
import com.bschmatz.cinecompass.data.models.PopularMovie
import com.bschmatz.cinecompass.data.models.RecommendationResponse
import com.bschmatz.cinecompass.data.models.TokenResponse
import javax.inject.Inject

class CineCompassRepository @Inject constructor(
    private val api: CineCompassApi
) {
    suspend fun login(username: String, password: String): Result<TokenResponse> =
        try {
            Result.success(api.login(LoginRequest(username, password)))
        } catch (e: Exception) {
            Result.failure(e)
        }

    suspend fun getRecommendations(
        token: String,
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
                    authorization = "Bearer $token"
                )
            )
        } catch (e: Exception) {
            Result.failure(e)
        }

    suspend fun submitRating(token: String, movieId: Int, rating: Double): Result<Unit> =
        try {
            Result.success(
                api.submitRating(
                    MovieRating(movieId = movieId, rating = rating),
                    authorization = "Bearer $token"
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
        token: String,
        ratings: List<MovieRating>
    ): Result<BatchRatingResponse> =
        try {
            val request = BatchRatingRequest(ratings)
            Result.success(api.submitBatchRatings(request, "Bearer $token"))
        } catch (e: Exception) {
            Result.failure(e)
        }
}