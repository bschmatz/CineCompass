package com.bschmatz.cinecompass.data.api

import com.bschmatz.cinecompass.data.models.BatchRatingRequest
import com.bschmatz.cinecompass.data.models.BatchRatingResponse
import com.bschmatz.cinecompass.data.models.MovieRating
import com.bschmatz.cinecompass.data.models.PopularMovie
import com.bschmatz.cinecompass.data.models.RecommendationResponse
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.Query


interface CineCompassApi {
    @GET("recommendations")
    suspend fun getRecommendations(
        @Query("page") page: Int,
        @Query("page_size") pageSize: Int,
        @Query("last_sync_time") lastSyncTime: String?,
        @Header("X-Session-ID") sessionId: String
    ): RecommendationResponse

    @POST("ratings")
    suspend fun submitRating(
        @Body rating: MovieRating,
        @Header("X-Session-ID") sessionId: String
    )

    @GET("movies/popular")
    suspend fun getPopularMovies(
        @Query("limit") limit: Int = 10
    ): List<PopularMovie>

    @POST("ratings/batch")
    suspend fun submitBatchRatings(
        @Body ratings: BatchRatingRequest,
        @Header("X-Session-ID") sessionId: String
    ): BatchRatingResponse

    @POST("refresh-session")
    suspend fun refreshSession(
        @Header("X-Session-ID") sessionId: String
    )

    @GET("is-onboarded")
    suspend fun isOnboarded(
        @Header("X-Session-ID") sessionId: String
    ): Boolean
}