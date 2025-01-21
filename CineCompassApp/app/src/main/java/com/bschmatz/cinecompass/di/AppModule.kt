package com.bschmatz.cinecompass.di

import android.content.Context
import com.bschmatz.cinecompass.data.local.TokenManager
import com.google.gson.Gson
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideTokenManager(@ApplicationContext context: Context, gson: Gson): TokenManager {
        return TokenManager(context, gson)
    }
}