package com.bschmatz.cinecompass.data.repository

import com.bschmatz.cinecompass.data.api.CineCompassApi
import com.bschmatz.cinecompass.data.models.LoginRequest
import com.bschmatz.cinecompass.data.models.RecommendationRequest
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
        request: RecommendationRequest
    ): Result<RecommendationResponse> =
        try {
            Result.success(api.getRecommendations(request, "Bearer $token"))
        } catch (e: Exception) {
            Result.failure(e)
        }
}