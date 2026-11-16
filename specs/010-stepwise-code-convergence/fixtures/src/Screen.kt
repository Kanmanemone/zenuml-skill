package com.shop.ui

@Composable
fun Screen(vm: ScreenViewModel = viewModel()) {
    val state by vm.state.collectAsState()
    Screen(state = state, onRefresh = vm::refresh)
}

@Composable
private fun Screen(state: ScreenState, onRefresh: () -> Unit) {
    Column {
        Text(state.title)
        Button(onClick = onRefresh) { Text("새로고침 {}") }
    }
}
