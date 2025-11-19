package com.bschmatz.cinecompass.data.local

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "session_prefs")

@Singleton
class SessionManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val dataStore = context.dataStore

    companion object {
        private val SESSION_KEY = stringPreferencesKey("session_id")
    }

    /**
     * Get or create session ID
     * Automatically generates a new UUID if no session exists
     */
    val sessionFlow: Flow<String> = dataStore.data.map { preferences ->
        preferences[SESSION_KEY] ?: generateAndSaveSession()
    }

    /**
     * Get session ID synchronously (for use in suspend functions)
     */
    suspend fun getSessionId(): String {
        return sessionFlow.first()
    }

    private suspend fun generateAndSaveSession(): String {
        val sessionId = UUID.randomUUID().toString()
        saveSession(sessionId)
        return sessionId
    }

    private suspend fun saveSession(sessionId: String) {
        dataStore.edit { preferences ->
            preferences[SESSION_KEY] = sessionId
        }
    }

    suspend fun clearSession() {
        dataStore.edit { preferences ->
            preferences.remove(SESSION_KEY)
        }
    }
}
