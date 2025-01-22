package com.bschmatz.cinecompass.data.models

import com.google.gson.annotations.SerializedName

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
    val director: String,
    @SerializedName("poster_path")
    val posterPath: String?,
    @SerializedName("backdrop_path")
    val backdropPath: String?,
    val overview: String,
    @SerializedName("vote_average")
    val voteAverage: Double,
    val popularity: Double,
    var userRating: Double = 0.0,
)

data class RecommendationResponse(
    val items: List<Recommendation>,
    val total: Int,
    val page: Int,
    @SerializedName("page_size")
    val pageSize: Int,
    @SerializedName("needs_sync")
    val needsSync: Boolean?,
    @SerializedName("new_ratings")
    val newRatings: List<MovieRating>
)