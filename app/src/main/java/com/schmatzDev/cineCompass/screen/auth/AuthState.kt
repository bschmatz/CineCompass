package com.schmatzDev.cineCompass.screen.auth

import com.google.firebase.auth.FirebaseUser

sealed class AuthState {
    object Initial : AuthState()
    object Loading : AuthState()
    object Unauthenticated : AuthState()
    data class Authenticated(val user: FirebaseUser) : AuthState()
    data class Error(val message: String) : AuthState()
}
