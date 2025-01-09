package com.bschmatz.cinecompass.data.models

import com.google.gson.annotations.SerializedName

data class RecommendationRequest(
    val ratings: List<MovieRating>,
    val page: Int = 1,
    @SerializedName("page_size")
    val pageSize: Int = 25,
    @SerializedName("force_refresh")
    val forceRefresh: Boolean = false
)

data class MovieRating(
    @SerializedName("movie_id")
    val movieId: Int,
    val rating: Double
)

data class Recommendation(
    val id: Int,
    val title: String,
    @SerializedName("similarity_score")
    val similarityScore: Double,
    val genres: List<String>,
    val cast: List<String>,
    val directory: String
)

data class RecommendationResponse(
    val items: List<Recommendation>,
    val total: Int,
    val page: Int,
    @SerializedName("page_size")
    val pageSize: Int
)