package com.example.nav3sample.entries

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation3.runtime.EntryProviderScope
import androidx.navigation3.runtime.entry
import com.example.nav3sample.navigation.AppNavKey
import com.example.nav3sample.navigation.SettingsRoute

/** Registers the Settings entry. Mirrors BookmarksEntryProvider. */
fun settingsEntryProvider(): EntryProviderScope<AppNavKey>.() -> Unit = {
    entry<SettingsRoute> {
        SettingsScreen()
    }
}

@Composable
private fun SettingsScreen() {
    Column(modifier = Modifier.padding(16.dp)) {
        Text("Settings")
    }
}
