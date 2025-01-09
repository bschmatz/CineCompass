package com.bschmatz.cinecompass.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bschmatz.cinecompass.data.local.TokenManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val tokenManager: TokenManager
) : ViewModel() {

    fun logout(onLogout: () -> Unit) {
        viewModelScope.launch {
            tokenManager.clearToken()
            onLogout()
        }
    }
}