package com.example.nav3sample.ui

import androidx.compose.runtime.Composable
import androidx.navigation3.runtime.EntryProviderScope
import androidx.navigation3.runtime.entryProvider
import androidx.navigation3.ui.NavDisplay
import com.example.nav3sample.entries.detailEntryProvider
import com.example.nav3sample.entries.homeEntryProvider
import com.example.nav3sample.entries.settingsEntryProvider
import com.example.nav3sample.navigation.AppNavKey
import com.example.nav3sample.navigation.AppNavigator
import com.example.nav3sample.navigation.AppNavigatorState

/** Adapts the project's back stack to androidx NavDisplay. Mirrors NiaNavDisplay. */
@Composable
fun AppNavDisplay(navigator: AppNavigator, state: AppNavigatorState) {
    val entryProviderBuilders: List<EntryProviderScope<AppNavKey>.() -> Unit> = listOf(
        homeEntryProvider(navigator),
        settingsEntryProvider(),
        detailEntryProvider(navigator),
    )

    NavDisplay(
        backStack = state.currentBackStack,
        onBack = { navigator.pop() },
        entryProvider = entryProvider { entryProviderBuilders.forEach { builder -> builder() } },
    )
}
