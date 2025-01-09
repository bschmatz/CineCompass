package com.bschmatz.cinecompass.ui.screens

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.bschmatz.cinecompass.ui.components.BottomBar
import com.bschmatz.cinecompass.ui.navigation.Screen

@Composable
fun MainScreen(onLogout: () -> Unit) {
    val navController = rememberNavController()

    Scaffold(
        bottomBar = { BottomBar(navController) }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = Screen.Home.route,
            modifier = Modifier.padding(paddingValues)
        ) {
            composable(Screen.Home.route) {
                HomeScreen()
            }
            composable(Screen.Profile.route) {
                ProfileScreen(onLogout = onLogout)
            }
        }
    }
}