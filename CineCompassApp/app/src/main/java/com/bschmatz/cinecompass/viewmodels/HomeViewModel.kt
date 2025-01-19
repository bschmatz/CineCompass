package com.bschmatz.cinecompass.viewmodels

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bschmatz.cinecompass.data.local.TokenManager
import com.bschmatz.cinecompass.data.models.Recommendation
import com.bschmatz.cinecompass.data.repository.CineCompassRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.launch
import java.time.LocalDateTime
import javax.inject.Inject

data class HomeState(
    val recommendations: List<Recommendation> = emptyList(),
    val currentIndex: Int = 0,
    val isLoading: Boolean = false,
    val error: String? = null,
    val hasMoreContent: Boolean = true,
    val ratings: MutableMap<Int, Double> = mutableMapOf()
)

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: CineCompassRepository,
    private val tokenManager: TokenManager
) : ViewModel() {

    var state by mutableStateOf(HomeState())
        private set

    private var currentPage = 1
    private val pageSize = 20
    private var isLoadingMore = false
    private var lastSyncTime: String? = null


    init {
        loadInitialRecommendations()
    }

    private fun loadInitialRecommendations() {
        viewModelScope.launch {
            state = state.copy(isLoading = true)
            fetchRecommendations()
        }
    }

    private suspend fun fetchRecommendations() {
        tokenManager.tokenFlow.firstOrNull()?.let { token ->
            try {
                repository.getRecommendations(
                    token = token,
                    page = currentPage,
                    pageSize = pageSize,
                    lastSyncTime = lastSyncTime
                ).onSuccess { response ->
                    val newRecommendations = if (currentPage == 1) {
                        response.items
                    } else {
                        state.recommendations + response.items
                    }

                    state = state.copy(
                        recommendations = newRecommendations,
                        isLoading = false,
                        error = null,
                        hasMoreContent = response.items.size >= pageSize
                    )

                    lastSyncTime = LocalDateTime.now().toString()

                }.onFailure { exception ->
                    state = state.copy(
                        isLoading = false,
                        error = exception.message
                    )
                }
            } catch (e: Exception) {
                state = state.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }

    fun onMovieSwiped() {
        if (state.currentIndex >= state.recommendations.size - 3 && !isLoadingMore && state.hasMoreContent) {
            loadMoreContent()
        }
        state = state.copy(currentIndex = state.currentIndex + 1)
    }

    private fun loadMoreContent() {
        if (isLoadingMore || !state.hasMoreContent) return

        viewModelScope.launch {
            isLoadingMore = true
            currentPage++
            fetchRecommendations()
            isLoadingMore = false
        }
    }

    fun onRatingChanged(movieId: Int, rating: Double) {
        viewModelScope.launch {
            tokenManager.tokenFlow.firstOrNull()?.let { token ->
                try {
                    repository.submitRating(token, movieId, rating)
                        .onSuccess {
                            state = state.copy(
                                ratings = state.ratings.toMutableMap().apply {
                                    put(movieId, rating)
                                }
                            )
                            currentPage = 1
                            fetchRecommendations()
                        }
                } catch (e: Exception) {
                    // Handle error
                    state = state.copy(error = e.message)
                }
            }
        }
    }

    fun refresh() {
        viewModelScope.launch {
            currentPage = 1
            fetchRecommendations()
        }
    }
}