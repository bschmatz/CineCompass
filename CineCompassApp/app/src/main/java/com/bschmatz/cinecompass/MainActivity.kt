package com.bschmatz.cinecompass

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import com.bschmatz.cinecompass.ui.screens.LoginScreen
import com.bschmatz.cinecompass.ui.screens.MainScreen
import com.bschmatz.cinecompass.ui.theme.CineCompassTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            CineCompassTheme {
                var isLoggedIn by remember { mutableStateOf(false) }

                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    if (!isLoggedIn) {
                        LoginScreen(onLoginSuccess = { isLoggedIn = true })
                    } else {
                        MainScreen(onLogout = { isLoggedIn = false })
                    }
                }
            }
        }
    }
}