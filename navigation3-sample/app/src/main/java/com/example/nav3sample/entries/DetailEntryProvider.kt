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

/** Registers the Detail entry, pushed on top of Home's back stack. Mirrors TopicEntryProvider. */
fun detailEntryProvider(navigator: AppNavigator): EntryProviderScope<AppNavKey>.() -> Unit = {
    entry<DetailRoute> { route ->
        DetailScreen(id = route.id, onBackClick = navigator::pop)
    }
}

@Composable
private fun DetailScreen(id: String, onBackClick: () -> Unit) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text("Detail $id")
        Button(onClick = onBackClick) {
            Text("Back")
        }
    }
}
