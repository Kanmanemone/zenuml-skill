package com.example.nav3sample.navigation

import androidx.compose.runtime.mutableStateListOf

/** navigate()/pop() API over [AppNavigatorState]. Mirrors NiaNavigator. */
class AppNavigator(private val state: AppNavigatorState) {

    fun navigate(key: AppNavKey) {
        if (key.isTopLevel) {
            if (key != state.currentTopLevelKey) {
                state.activeTopLevelKeys.remove(key)
                state.activeTopLevelKeys.add(key)
                state.backStacks.getOrPut(key) { mutableStateListOf(key) }
            }
        } else {
            state.currentBackStack.add(key)
        }
    }

    fun pop() {
        val currentStack = state.currentBackStack
        if (currentStack.size > 1) {
            currentStack.removeAt(currentStack.lastIndex)
        } else if (state.activeTopLevelKeys.size > 1) {
            state.activeTopLevelKeys.removeAt(state.activeTopLevelKeys.lastIndex)
        }
    }
}
