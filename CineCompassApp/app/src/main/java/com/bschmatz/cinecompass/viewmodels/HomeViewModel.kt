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
import java.time.LocalDateTime
import javax.inject.Inject

data class HomeState(
    val recommendations: List<Recommendation> = emptyList(),
    val currentIndex: Int = 0,
    val isLoading: Boolean = false,
    val error: String? = null,
    val hasMoreContent: Boolean = true,
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
    private var ratingJob: Job? = null
    private var backgroundRefreshJob: Job? = null

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
                state = state.copy(isLoading = true)
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

                    if (response.needsSync == true && response.items.isNotEmpty()) {
                        lastSyncTime = LocalDateTime.now().toString()
                    } else if (response.needsSync == true && response.items.isEmpty()) {
                        delay(500)
                        fetchRecommendations()
                    }
                }
            } catch (e: Exception) {
                state = state.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }

    private fun scheduleBackgroundRefresh() {
        backgroundRefreshJob?.cancel()
        backgroundRefreshJob = viewModelScope.launch {
            delay(500) // Small delay to ensure rating is processed
            refresh()
        }
    }

    fun setCurrentIndex(index: Int) {
        state = state.copy(currentIndex = index)
        if (index >= state.recommendations.size - 3 && !isLoadingMore && state.hasMoreContent) {
            loadMoreContent()
        }
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
        ratingJob?.cancel()
        ratingJob = viewModelScope.launch {
            delay(1000) // Debounce
            tokenManager.tokenFlow.firstOrNull()?.let { token ->
                try {
                    repository.submitRating(token, movieId, rating)
                        .onSuccess {
                            // The next recommendations request will handle the refresh
                            lastSyncTime = LocalDateTime.now().toString()
                        }
                } catch (e: Exception) {
                    state = state.copy(error = e.message)
                }
            }
        }
    }

    fun refresh() {
        viewModelScope.launch {
            currentPage = 1
            state = state.copy(isLoading = true)
            fetchRecommendations()
        }
    }

    override fun onCleared() {
        super.onCleared()
        ratingJob?.cancel()
        backgroundRefreshJob?.cancel()
    }
}