package com.example.nav3sample

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.remember
import com.example.nav3sample.navigation.AppNavigator
import com.example.nav3sample.navigation.AppNavigatorState
import com.example.nav3sample.navigation.HomeRoute
import com.example.nav3sample.ui.App

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val state = remember { AppNavigatorState(startKey = HomeRoute) }
            val navigator = remember(state) { AppNavigator(state) }
            MaterialTheme {
                Surface {
                    App(navigator = navigator, state = state)
                }
            }
        }
    }
}
