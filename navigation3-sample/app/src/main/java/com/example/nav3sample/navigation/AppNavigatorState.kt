package com.example.nav3sample.navigation

import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.snapshots.SnapshotStateList

/** Holds the per-tab back stacks. Mirrors NiaNavigatorState. */
class AppNavigatorState(startKey: AppNavKey) {

    val activeTopLevelKeys: SnapshotStateList<AppNavKey> = mutableStateListOf(startKey)

    val backStacks = mutableStateMapOf<AppNavKey, SnapshotStateList<AppNavKey>>(
        startKey to mutableStateListOf(startKey),
    )

    val currentTopLevelKey: AppNavKey
        get() = activeTopLevelKeys.last()

    val currentBackStack: SnapshotStateList<AppNavKey>
        get() = backStacks.getValue(currentTopLevelKey)
}
