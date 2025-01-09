package com.bschmatz.cinecompass.data.local

import android.content.Context
import android.util.Base64
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.google.gson.Gson
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "auth_prefs")

@Singleton
class TokenManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val gson: Gson
) {
    private val dataStore = context.dataStore

    companion object {
        private val TOKEN_KEY = stringPreferencesKey("jwt_token")
    }

    private fun decodeJWT(token: String): JWTPayload? {
        return try {
            val parts = token.split(".")
            if (parts.size != 3) return null
            val payload = String(Base64.decode(parts[1], Base64.URL_SAFE))
            gson.fromJson(payload, JWTPayload::class.java)
        } catch (e: Exception) {
            null
        }
    }

    private fun isTokenValid(token: String): Boolean {
        val payload = decodeJWT(token) ?: return false
        return payload.exp * 1000 > System.currentTimeMillis()
    }

    suspend fun saveToken(token: String) {
        dataStore.edit { preferences ->
            preferences[TOKEN_KEY] = token
        }
    }

    val tokenFlow: Flow<String?> = dataStore.data.map { preferences ->
        val token = preferences[TOKEN_KEY]
        if (token != null && isTokenValid(token)) {
            token
        } else {
            clearToken()
            null
        }
    }

    suspend fun clearToken() {
        dataStore.edit { preferences ->
            preferences.remove(TOKEN_KEY)
        }
    }
}

private data class JWTPayload(
    val exp: Long,
    val sub: String
)