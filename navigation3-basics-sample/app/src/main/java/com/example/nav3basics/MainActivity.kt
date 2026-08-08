package com.example.nav3basics

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation3.runtime.entry
import androidx.navigation3.runtime.entryProvider
import androidx.navigation3.ui.NavDisplay

// Keys are plain objects, exactly as the official docs model a back stack:
// https://developer.android.com/guide/navigation/navigation-3/basics
data object Home
data class Product(val id: String)
data object About

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface {
                    NavExample()
                }
            }
        }
    }
}

@Composable
private fun NavExample() {
    // The back stack is just a list of keys — no custom wrapper type.
    val backStack = remember { mutableStateListOf<Any>(Home) }

    NavDisplay(
        backStack = backStack,
        onBack = { backStack.removeLastOrNull() },
        entryProvider = entryProvider {
            entry<Home> {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Home")
                    Button(onClick = { backStack.add(Product(id = "123")) }) {
                        Text("Go to product")
                    }
                    Button(onClick = { backStack.add(About) }) {
                        Text("About")
                    }
                }
            }
            entry<Product> { product ->
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Product ${product.id}")
                    Button(onClick = { backStack.removeLastOrNull() }) {
                        Text("Back")
                    }
                }
            }
            entry<About> {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("About")
                    Button(onClick = { backStack.removeLastOrNull() }) {
                        Text("Back")
                    }
                }
            }
        },
    )
}
