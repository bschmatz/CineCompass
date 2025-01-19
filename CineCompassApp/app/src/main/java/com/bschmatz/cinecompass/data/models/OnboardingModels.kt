package com.bschmatz.cinecompass.data.models

import com.google.gson.annotations.SerializedName

data class PopularMovie(
    val id: Int,
    val title: String,
    val overview: String,
    val genres: List<String>,
    @SerializedName("poster_path")
    val posterPath: String?,
    @SerializedName("vote_average")
    val voteAverage: Double,
    val popularity: Double
)

data class BatchRatingRequest(
    val ratings: List<MovieRating>
)

data class BatchRatingResponse(
    val status: String,
    val message: String
)