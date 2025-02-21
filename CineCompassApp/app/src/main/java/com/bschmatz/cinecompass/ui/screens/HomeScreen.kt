package com.bschmatz.cinecompass.ui.screens

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.pager.VerticalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.material.ExperimentalMaterialApi
import androidx.compose.material.pullrefresh.PullRefreshIndicator
import androidx.compose.material.pullrefresh.pullRefresh
import androidx.compose.material.pullrefresh.rememberPullRefreshState
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import com.bschmatz.cinecompass.data.models.Recommendation
import com.bschmatz.cinecompass.ui.components.MovieCard
import com.bschmatz.cinecompass.ui.components.PosterView
import com.bschmatz.cinecompass.viewmodels.HomeViewModel

@OptIn(ExperimentalMaterialApi::class)
@Composable
fun HomeScreen(
    viewModel: HomeViewModel = hiltViewModel()
) {
    val state = viewModel.state
    var showFullPoster by remember { mutableStateOf(false) }
    var selectedMovie by remember { mutableStateOf<Recommendation?>(null) }

    Box(modifier = Modifier.fillMaxSize()) {
        if (state.recommendations.isNotEmpty()) {
            val pullRefreshState = rememberPullRefreshState(
                refreshing = state.isRefreshing,
                onRefresh = viewModel::refreshRecommendations
            )

            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .pullRefresh(pullRefreshState)
            ) {
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
                            state.recommendations[page].userRating = rating
                        },
                        onPosterClick = {
                            if (movie.posterPath != null) {
                                selectedMovie = movie
                                showFullPoster = true
                            }
                        },
                        modifier = Modifier.fillMaxSize()
                    )
                }

                PullRefreshIndicator(
                    refreshing = state.isRefreshing,
                    state = pullRefreshState,
                    modifier = Modifier.align(Alignment.TopCenter)
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

        if (showFullPoster && selectedMovie != null && selectedMovie?.posterPath != null) {
            PosterView(
                posterPath = selectedMovie!!.posterPath!!,
                movieTitle = selectedMovie!!.title,
                onDismiss = {
                    showFullPoster = false
                    selectedMovie = null
                }
            )
        }
    }
}