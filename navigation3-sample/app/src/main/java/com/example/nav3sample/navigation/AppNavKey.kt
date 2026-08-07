package com.example.nav3sample.navigation

/** Contract every destination key must satisfy. Mirrors NiaNavKey. */
interface AppNavKey {
    val isTopLevel: Boolean
}

data object HomeRoute : AppNavKey {
    override val isTopLevel = true
}

data object SettingsRoute : AppNavKey {
    override val isTopLevel = true
}

data class DetailRoute(val id: String) : AppNavKey {
    override val isTopLevel = false
}
