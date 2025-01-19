package com.bschmatz.cinecompass.data.local

import android.content.Context
import javax.inject.Inject

class OnboardingManager @Inject constructor(
    private val context: Context
) {
    private val prefs = context.getSharedPreferences("onboarding_prefs", Context.MODE_PRIVATE)

    fun hasCompletedOnboarding(): Boolean {
        return prefs.getBoolean("completed_onboarding", false)
    }

    fun setOnboardingCompleted() {
        prefs.edit().putBoolean("completed_onboarding", true).apply()
    }
}