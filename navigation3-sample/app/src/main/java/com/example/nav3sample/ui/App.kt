package com.example.nav3sample.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.nav3sample.navigation.AppNavigator
import com.example.nav3sample.navigation.AppNavigatorState
import com.example.nav3sample.navigation.HomeRoute
import com.example.nav3sample.navigation.SettingsRoute

/** Top-level shell: tab switcher + the current tab's NavDisplay. Mirrors NiaApp. */
@Composable
fun App(navigator: AppNavigator, state: AppNavigatorState) {
    Column {
        Row(modifier = Modifier.padding(8.dp)) {
            Button(onClick = { navigator.navigate(HomeRoute) }) { Text("Home") }
            Button(onClick = { navigator.navigate(SettingsRoute) }) { Text("Settings") }
        }
        AppNavDisplay(navigator = navigator, state = state)
    }
}
