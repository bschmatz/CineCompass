package com.bschmatz.cinecompass.ui.screens

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.pager.VerticalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import com.bschmatz.cinecompass.ui.components.MovieCard
import com.bschmatz.cinecompass.viewmodels.HomeViewModel

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun HomeScreen(
    viewModel: HomeViewModel = hiltViewModel()
) {
    val state = viewModel.state

    Box(modifier = Modifier.fillMaxSize()) {
        if (state.recommendations.isNotEmpty()) {
            val pagerState = rememberPagerState(
                initialPage = 0,
                pageCount = { state.recommendations.size }
            )

            LaunchedEffect(pagerState.currentPage) {
                viewModel.setCurrentIndex(pagerState.currentPage)
            }

            VerticalPager(
                state = pagerState,
                modifier = Modifier.fillMaxSize(),
                key = { state.recommendations[it].id }
            ) { page ->
                val movie = state.recommendations[page]
                MovieCard(
                    movie = movie,
                    onRatingChanged = { rating ->
                        viewModel.onRatingChanged(movie.id, rating)
                    },
                    modifier = Modifier.fillMaxSize()
                )
            }
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
                modifier = Modifier.align(Alignment.Center)
            )
        }
    }
}