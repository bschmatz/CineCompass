package com.bschmatz.cinecompass.data.api

import com.bschmatz.cinecompass.data.models.LoginRequest
import com.bschmatz.cinecompass.data.models.RecommendationRequest
import com.bschmatz.cinecompass.data.models.RecommendationResponse
import com.bschmatz.cinecompass.data.models.RegisterRequest
import com.bschmatz.cinecompass.data.models.TokenResponse
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.POST


interface CineCompassApi {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): TokenResponse

    @POST("auth/register")
    suspend fun register(@Body request: RegisterRequest): TokenResponse

    @POST("recommendations")
    suspend fun getRecommendations(
        @Body request: RecommendationRequest,
        @Header("Authorization") authorization: String
    ): RecommendationResponse
}