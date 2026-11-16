@Composable
fun Screen(vm: ScreenViewModel = viewModel()) {
    val state by vm.state.collectAsState()
    Screen(state = state, onRefresh = vm::refresh)
}
