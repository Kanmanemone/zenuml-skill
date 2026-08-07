package com.example.nav3sample.entries

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation3.runtime.EntryProviderScope
import androidx.navigation3.runtime.entry
import com.example.nav3sample.navigation.AppNavKey
import com.example.nav3sample.navigation.AppNavigator
import com.example.nav3sample.navigation.DetailRoute
import com.example.nav3sample.navigation.HomeRoute

/** Registers the Home entry. Mirrors ForYouEntryProvider. */
fun homeEntryProvider(navigator: AppNavigator): EntryProviderScope<AppNavKey>.() -> Unit = {
    entry<HomeRoute> {
        HomeScreen(onDetailClick = { navigator.navigate(DetailRoute(id = "42")) })
    }
}

@Composable
private fun HomeScreen(onDetailClick: () -> Unit) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text("Home")
        Button(onClick = onDetailClick) {
            Text("Open detail")
        }
    }
}
