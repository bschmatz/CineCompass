package com.bschmatz.cinecompass.ui.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.bschmatz.cinecompass.viewmodels.ProfileViewModel
import kotlinx.coroutines.runBlocking

@Composable
fun ProfileScreen(
    profileViewModel: ProfileViewModel = hiltViewModel(),
    onLogout: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "Profile",
            style = MaterialTheme.typography.headlineMedium
        )
        Button(
            onClick = {
                runBlocking { profileViewModel.logout(onLogout) }
            },
            modifier = Modifier.padding(top = 16.dp)
        ) {
            Text("Logout")
        }
    }
}