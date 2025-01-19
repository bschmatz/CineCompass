package com.bschmatz.cinecompass.ui.screens

import androidx.compose.foundation.gestures.Orientation
import androidx.compose.foundation.gestures.draggable
import androidx.compose.foundation.gestures.rememberDraggableState
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.wear.compose.material.ExperimentalWearMaterialApi
import androidx.wear.compose.material.FractionalThreshold
import androidx.wear.compose.material.rememberSwipeableState
import androidx.wear.compose.material.swipeable
import com.bschmatz.cinecompass.ui.components.MovieCard
import com.bschmatz.cinecompass.viewmodels.HomeViewModel

@OptIn(ExperimentalWearMaterialApi::class)
@Composable
fun HomeScreen(
    viewModel: HomeViewModel = hiltViewModel()
) {
    val state = viewModel.state
    val density = LocalDensity.current

    Box(modifier = Modifier.fillMaxSize()) {
        if (state.recommendations.isNotEmpty() && state.currentIndex < state.recommendations.size) {
            val currentMovie = state.recommendations[state.currentIndex]
            val swipeableState = rememberSwipeableState(0)

            val anchors = mapOf(
                0f to 0,
                with(density) { -1000.dp.toPx() } to 1
            )

            MovieCard(
                movie = currentMovie,
                onRatingChanged = { rating ->
                    viewModel.onRatingChanged(currentMovie.id, rating)
                },
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp)
                    .swipeable(
                        state = swipeableState,
                        anchors = anchors,
                        thresholds = { _, _ -> FractionalThreshold(0.3f) },
                        orientation = Orientation.Horizontal
                    )
                    .draggable(
                        orientation = Orientation.Horizontal,
                        state = rememberDraggableState { delta ->
                            if (delta < -50) {
                                viewModel.onMovieSwiped()
                            }
                        }
                    )
            )
        }

        if (state.isLoading && state.recommendations.isEmpty()) {
            CircularProgressIndicator(
                modifier = Modifier.align(Alignment.Center)
            )
        }

        state.error?.let { error ->
            Text(
                text = error,
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier
                    .align(Alignment.Center)
                    .padding(16.dp)
            )
        }
    }
}