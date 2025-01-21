package com.bschmatz.cinecompass.viewmodels

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bschmatz.cinecompass.data.local.TokenManager
import com.bschmatz.cinecompass.data.models.MovieRating
import com.bschmatz.cinecompass.data.models.PopularMovie
import com.bschmatz.cinecompass.data.repository.CineCompassRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.launch
import javax.inject.Inject

data class OnboardingState(
    val movies: List<PopularMovie> = emptyList(),
    val ratings: Map<Int, Double> = emptyMap(),
    val isLoading: Boolean = false,
    val isSubmitting: Boolean = false,
    val error: String? = null,
    val onboardingCompleted: Boolean = false
)

@HiltViewModel
class OnboardingViewModel @Inject constructor(
    private val repository: CineCompassRepository,
    private val tokenManager: TokenManager
) : ViewModel() {

    var state by mutableStateOf(OnboardingState())
        private set

    init {
        loadPopularMovies()
    }

    private fun loadPopularMovies() {
        viewModelScope.launch {
            state = state.copy(isLoading = true)
            repository.getPopularMovies(10)
                .onSuccess { movies ->
                    state = state.copy(
                        movies = movies,
                        isLoading = false
                    )
                }
                .onFailure { exception ->
                    state = state.copy(
                        error = exception.message,
                        isLoading = false
                    )
                }
        }
    }

    fun onRatingChanged(movieId: Int, rating: Double) {
        println("Rating changed: Movie $movieId to rating $rating")

        state = state.copy(
            ratings = state.ratings.toMutableMap().apply {
                put(movieId, rating)
            }
        )

        println("New ratings state: ${state.ratings}")
    }

    fun submitRatings() {
        if (state.ratings.size < 5) {
            state = state.copy(error = "Please rate at least 5 movies")
            return
        }

        viewModelScope.launch {
            state = state.copy(isSubmitting = true)
            val ratings = state.ratings.map { (movieId, rating) ->
                MovieRating(movieId = movieId, rating = rating)
            }

            tokenManager.tokenFlow.firstOrNull()?.let { token ->
                repository.submitBatchRatings(token, ratings)
                    .onSuccess {
                        state = state.copy(
                            isSubmitting = false,
                            onboardingCompleted = true
                        )
                    }
                    .onFailure { exception ->
                        state = state.copy(
                            isSubmitting = false,
                            error = exception.message
                        )
                    }
            }
        }
    }
}