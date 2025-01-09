package com.bschmatz.cinecompass.viewmodels

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bschmatz.cinecompass.data.local.TokenManager
import com.bschmatz.cinecompass.data.repository.CineCompassRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val repository: CineCompassRepository,
    private val tokenManager: TokenManager
) : ViewModel() {
    var state by mutableStateOf(LoginState())
        private set

    init {
        viewModelScope.launch {
            tokenManager.tokenFlow.collect { token ->
                if (token != null) {
                    state = state.copy(isLoggedIn = true, token = token)
                }
            }
        }
    }

    fun onUsernameChange(username: String) {
        state = state.copy(username = username)
    }

    fun onPasswordChange(password: String) {
        state = state.copy(password = password)
    }

    fun login() {
        viewModelScope.launch {
            state = state.copy(isLoading = true, error = null)
            repository.login(state.username, state.password)
                .onSuccess { response ->
                    tokenManager.saveToken(response.accessToken)
                    state = state.copy(
                        isLoading = false,
                        isLoggedIn = true,
                        token = response.accessToken
                    )
                }
                .onFailure { exception ->
                    state = state.copy(
                        isLoading = false,
                        error = exception.message
                    )
                }
        }
    }
}

data class LoginState(
    val username: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val isLoggedIn: Boolean = false,
    val token: String? = null,
    val error: String? = null
)