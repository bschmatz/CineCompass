package com.bschmatz.cinecompass.data.api

import com.bschmatz.cinecompass.data.models.BatchRatingRequest
import com.bschmatz.cinecompass.data.models.BatchRatingResponse
import com.bschmatz.cinecompass.data.models.LoginRequest
import com.bschmatz.cinecompass.data.models.MovieRating
import com.bschmatz.cinecompass.data.models.PopularMovie
import com.bschmatz.cinecompass.data.models.RecommendationResponse
import com.bschmatz.cinecompass.data.models.RegisterRequest
import com.bschmatz.cinecompass.data.models.TokenResponse
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.Query


interface CineCompassApi {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): TokenResponse

    @POST("auth/register")
    suspend fun register(@Body request: RegisterRequest): TokenResponse

    @GET("recommendations")
    suspend fun getRecommendations(
        @Query("page") page: Int,
        @Query("page_size") pageSize: Int,
        @Query("last_sync_time") lastSyncTime: String?,
        @Header("Authorization") authorization: String
    ): RecommendationResponse

    @POST("ratings")
    suspend fun submitRating(
        @Body rating: MovieRating,
        @Header("Authorization") authorization: String
    )

    @GET("movies/popular")
    suspend fun getPopularMovies(
        @Query("limit") limit: Int = 10
    ): List<PopularMovie>

    @POST("ratings/batch")
    suspend fun submitBatchRatings(
        @Body ratings: BatchRatingRequest,
        @Header("Authorization") authorization: String
    ): BatchRatingResponse
}