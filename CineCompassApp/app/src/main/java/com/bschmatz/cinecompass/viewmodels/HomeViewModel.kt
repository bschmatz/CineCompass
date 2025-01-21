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
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HomeState(
    val recommendations: List<Recommendation> = emptyList(),
    val currentIndex: Int = 0,
    val isLoading: Boolean = false,
    val error: String? = null,
    val hasMoreContent: Boolean = true,
    val isRefreshing: Boolean = false
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
    private var ratingJob: Job? = null
    private var fetchJob: Job? = null

    init {
        loadInitialRecommendations()
    }

    private fun loadInitialRecommendations() {
        viewModelScope.launch {
            state = state.copy(isLoading = true)
            fetchRecommendations(isInitial = true)
        }
    }

    fun refreshRecommendations() {
        viewModelScope.launch {
            state = state.copy(isRefreshing = true)
            tokenManager.tokenFlow.firstOrNull()?.let { token ->
                try {
                    repository.refreshSessions(token).onSuccess {
                        currentPage = 1
                        fetchRecommendations(isInitial = true)
                    }.onFailure { e ->
                        state = state.copy(
                            isRefreshing = false,
                            error = e.message
                        )
                    }
                } catch (e: Exception) {
                    state = state.copy(
                        isRefreshing = false,
                        error = e.message
                    )
                }
            }
        }
    }

    private fun fetchRecommendations(isInitial: Boolean = false) {
        if (fetchJob?.isActive == true) return

        fetchJob = viewModelScope.launch {
            tokenManager.tokenFlow.firstOrNull()?.let { token ->
                try {
                    val response = repository.getRecommendations(
                        token = token,
                        page = currentPage,
                        pageSize = pageSize,
                        lastSyncTime = null
                    ).getOrThrow()

                    val newRecommendations = when {
                        isInitial || currentPage == 1 -> response.items
                        else -> state.recommendations + response.items
                    }

                    state = state.copy(
                        recommendations = newRecommendations,
                        isLoading = false,
                        isRefreshing = false,
                        error = null,
                        hasMoreContent = response.items.size >= pageSize
                    )
                } catch (e: Exception) {
                    state = state.copy(
                        isLoading = false,
                        isRefreshing = false,
                        error = e.message
                    )
                }
            }
        }
    }

    fun setCurrentIndex(index: Int) {
        state = state.copy(currentIndex = index)
        if (index >= state.recommendations.size - 3 && !state.isLoading && state.hasMoreContent) {
            loadMoreContent()
        }
    }

    private fun loadMoreContent() {
        if (state.isLoading || !state.hasMoreContent) return

        viewModelScope.launch {
            currentPage++
            fetchRecommendations()
        }
    }

    fun onRatingChanged(movieId: Int, rating: Double) {
        ratingJob?.cancel()
        ratingJob = viewModelScope.launch {
            delay(500)
            tokenManager.tokenFlow.firstOrNull()?.let { token ->
                try {
                    repository.submitRating(token, movieId, rating)
                } catch (e: Exception) {
                    state = state.copy(error = e.message)
                }
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        ratingJob?.cancel()
        fetchJob?.cancel()
    }
}