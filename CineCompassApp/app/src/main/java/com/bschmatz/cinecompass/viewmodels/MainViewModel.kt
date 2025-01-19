package com.bschmatz.cinecompass.viewmodels

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import com.bschmatz.cinecompass.data.local.OnboardingManager
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class MainViewModel @Inject constructor(
    private val onboardingManager: OnboardingManager
) : ViewModel() {
    var state by mutableStateOf(MainState())
        private set

    init {
        state = state.copy(
            needsOnboarding = !onboardingManager.hasCompletedOnboarding()
        )
    }
}

data class MainState(
    val needsOnboarding: Boolean = true
)
