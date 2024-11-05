package com.schmatzDev.cineCompass

import AuthViewModel
import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.schmatzDev.cineCompass.screen.auth.AuthScreen
import com.schmatzDev.cineCompass.screen.home.HomeScreen

sealed class Screen(val route: String) {
    object Auth : Screen("auth")
    object Home : Screen("home")
}

@Composable
fun CineCompassNavigation(
    navController: NavHostController,
    viewModel: AuthViewModel
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Auth.route
    ) {
        composable(Screen.Auth.route) {
            AuthScreen(
                viewModel = viewModel,
                onAuthSuccess = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Auth.route) { inclusive = true }
                    }
                }
            )
        }

        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToMovies = {
                    println("Navigate to movies")
                },
                onNavigateToProfile = {
                    println("Navigate to profile")
                }
            )
        }
    }
}