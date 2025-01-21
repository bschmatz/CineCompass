package com.bschmatz.cinecompass.viewmodels

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bschmatz.cinecompass.data.local.TokenManager
import com.bschmatz.cinecompass.data.repository.CineCompassRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class MainViewModel @Inject constructor(
    private val repository: CineCompassRepository,
    private val tokenManager: TokenManager
) : ViewModel() {
    var state by mutableStateOf(MainState())
        private set

    init {
        checkOnboardingStatus()
    }

    private fun checkOnboardingStatus() {
        viewModelScope.launch {
            tokenManager.tokenFlow.firstOrNull()?.let { token ->
                repository.isOnboarded(token)
                    .onSuccess { isOnboarded ->
                        state = state.copy(needsOnboarding = !isOnboarded, isLoading = false)
                    }
                    .onFailure {
                        state = state.copy(needsOnboarding = true, isLoading = false)
                    }
            }
        }
    }
}

data class MainState(
    val needsOnboarding: Boolean = true,
    val isLoading: Boolean = true,
)