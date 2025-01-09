package com.bschmatz.cinecompass.ui.theme

import android.app.Activity
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// Deep purple theme colors
private val DeepPurple = Color(0xFF2A0944)
private val MediumPurple = Color(0xFF3B185F)
private val LightPurple = Color(0xFF7858A6)
private val AccentPurple = Color(0xFF9867C5)
private val SurfaceDark = Color(0xFF1A0629)
private val BackgroundDark = Color(0xFF12041D)

private val DarkColorScheme = darkColorScheme(
    primary = AccentPurple,
    secondary = LightPurple,
    tertiary = MediumPurple,
    background = BackgroundDark,
    surface = SurfaceDark,
    onPrimary = Color.White,
    onSecondary = Color.White,
    onTertiary = Color.White,
    onBackground = Color.White,
    onSurface = Color.White
)

private val LightColorScheme = DarkColorScheme

@Composable
fun CineCompassTheme(
    darkTheme: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = DarkColorScheme

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.background.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}