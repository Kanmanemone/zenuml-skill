"""Run from the repository root: python specs/010-stepwise-code-convergence/test_learning_stages.py.

Set REGENERATE=1 to rewrite fixtures/expected/*.md from the current output (then review the diff).
"""
import contextlib
import importlib.util
import io
import json
import os
import re
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace as Args
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('stages', ROOT / '.agents/skills/revealing-code-step-by-step/scripts/stages.py')
s = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(s)
FIXTURE = Path(__file__).parent / 'fixtures'

SHOP = '''class Shop @Inject constructor(
    private val repo: Repo,
    clock: Clock,
) : Base() {
    var busy by mutableStateOf(false)
    private var last: String? = null

    val items: Flow<List<Item>> =
        repo.items()
            .onStart { emit(emptyList()) }

    /** Buys one item. */
    fun buy(id: String) {
        busy = true
        last = id
        repo.buy(id, clock.now())
    }

    fun a() {}
    fun b() {}
    fun c() {}
}
'''
REPO = '''interface Repo {
    val items: Flow<List<Item>>

    fun buy(id: String)
    fun sell(id: String)
}
'''
MENU = '''@Composable
fun Menu(onClick: () -> Unit) {
    Box {
        Icon()

        DropdownMenu(onClick = onClick)
    }

    fun close() {
        val x = 1

        log(x)
    }
}
'''


def run(fn, **args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        fn(Args(**args))
    first, _, rest = out.getvalue().partition('\n')
    return json.loads(first), rest


def parsed_outline(result, manifest):
    outline = json.loads((result / 'work/outline.json').read_text(encoding='utf-8'))
    return {n['id']: s.check_outline(n, n['tree'], outline[n['id']])[1] for n in manifest['nodes'] if n['id'] in outline}


def exit_code(argv):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()), \
            unittest.TestCase().assertRaises(SystemExit) as failed:
        s.main(argv)
    return failed.exception.code


class Definition(unittest.TestCase):
    def test_kinds_in_order_and_notes_section_is_not_a_stage(self):
        stages = s.parse_stage_definition()
        self.assertEqual([x['kind'] for x in stages], list(s.KINDS))
        self.assertEqual([x['nickname'] for x in stages], ['사용 상황', '윤곽', '펼치기', '원본'])

    def test_hiding_and_unknown_names(self):
        planned, notices = s.plan_stages(s.parse_stage_definition(), {'윤곽': False, '없는 단계': True}, [], ['펼치기', '원본'])
        self.assertEqual([x['visible'] for x in planned], [True, False, False, True])
        self.assertEqual(len(notices), 2)


class Declarations(unittest.TestCase):
    def test_extension_declarations_are_found_by_name_not_receiver(self):
        text = '''private fun DrawScope.drawBullets(
    a: Int,
) {
    x()
}

fun <T> List<T>.second(): T = this[1]
'''
        self.assertEqual(s.find_declaration(text, ['drawBullets'])[0], (1, 5))
        self.assertEqual(s.find_declaration(text, ['second'])[0], (7, 7))
        self.assertIsNone(s.find_declaration(text, ['DrawScope'])[0])


RAW = '''object Key : EntryKey {
    override val title = "t"
    override val description = """
        body line
    """.trimIndent()
    override val screen = { Screen() }
}
'''


ANNOTATED = '''object Module {
    @Provides
    @IntoSet
    fun provide(): EntryKey = Key

    @OptIn(ExperimentalApi::class)
    override fun onCreate() {
        run()
    }
}
'''


NESTED = '''@Composable
fun Field(
    state: State,
    style: Style = Style(),
    onLayout: (() -> Unit)? = null,
) {
    /** One bullet's width. */
    val gutter = measure(style)

    var layout: Layout? by remember { mutableStateOf(null) }

    Basic(
        state = state,
        style = style,
        onLayout = { result ->
            layout = result
            onLayout?.invoke()
        },
        decorator = { inner ->
            val field = @Composable {
                Box(
                    Modifier
                        .clip()
                        .drawBehind {
                            layout?.let { l ->
                                val offset = scroll(l)
                                drawBullets(l, offset)
                            }
                        }
                        .padding(gutter),
                ) {
                    inner()
                }
            }
            field()
        },
    )
}
'''
FIVE = '''fun five() {
    a()
    b()
    c()
    d()
    e()
}
'''


def tree_of(text):
    return s.build_tree(text)


def auto_entry(tree, sentence='할 일을 마친다.'):
    """An outline entry keeping every child separate (at most four groups per scope)."""
    entry = []
    for scope in s.tree_scopes(tree):
        kids = list(range(1, len(s.tree_children(tree, scope)) + 1))
        size = -(-len(kids) // s.MAX_SEP)
        groups = [{'ids': kids[i:i + size], 's': sentence} for i in range(0, len(kids), size)]
        entry.append({'sep': groups} if scope == 'R' else {'s': sentence, 'sep': groups})
    return entry


def scenes_of(text, entry=None):
    tree = tree_of(text)
    errors, parsed = s.check_outline({'id': 'X'}, tree, entry or auto_entry(tree))
    assert not errors, errors
    steps = s.plan_steps(tree, parsed)
    lines = text.rstrip('\n').split('\n')
    at = s.attach_steps(tree, steps, lines, s.mask_code(text).rstrip('\n').split('\n'))
    return tree, steps, [s.render_steps_scene(tree, lines, steps, at, k) for k in range(len(steps) + 1)]


VM = '''class Vm(private val repo: Repo) {
    private val selected = MutableStateFlow(0)

    // the items of the selected id
    private val items: Flow<List<Item>> =
        selected
            .flatMapLatest { id ->
                if (id == 0) {
                    flowOf(emptyList())
                } else {
                    repo.items(id)
                }
            }
            .stateIn(scope, started, emptyList())

    val state = combine(items, selected) { items, selected ->
        State(items, selected)
    }
}
'''


SAMPLES = [NESTED, FIVE, SHOP, REPO, MENU, RAW, ANNOTATED, VM]


def all_texts():
    return SAMPLES + [p.read_text(encoding='utf-8') for p in (FIXTURE / 'expected/original').glob('*.kt')]


class Tree(unittest.TestCase):
    def test_own_line_annotations_attach_to_the_next_declaration(self):
        info = s.analyse(ANNOTATED)
        self.assertEqual([(it['name'], it['comments'], it['lines']) for it in info['items']],
                         [('provide', [1, 2], [3]), ('onCreate', [5], [6, 7, 8])])

    def test_multiline_raw_string_stays_in_one_item(self):
        info = s.analyse(RAW)
        self.assertEqual([(it['name'], it['lines']) for it in info['items']],
                         [('title', [1]), ('description', [2, 3, 4]), ('screen', [5])])

    def test_nested_scopes_split_by_block_arguments_and_chain(self):
        tree = tree_of(NESTED)
        self.assertEqual(len(s.tree_scopes(tree)), 7)
        lines = NESTED.split('\n')
        texts = [[lines[j].strip() for j in s.subtree_lines(tree, n)] for n in range(len(tree['nodes']))]
        self.assertIn(['state = state,', 'style = style,'], texts)  # one-line arguments merge
        chain = next(n for n, t in enumerate(texts) if t and t[0] == 'Modifier')
        self.assertEqual([lines[min(s.subtree_lines(tree, c))].strip()[:6] for c in tree['nodes'][chain]['children']],
                         ['.clip(', '.drawB', '.paddi'])
        self.assertEqual([a['name'] for a in tree['attached']], ['state', 'style', 'onLayout', 'layout'])

    def test_single_child_layers_merge_including_the_root(self):
        for text in all_texts():
            tree = tree_of(text)
            if tree:
                self.assertTrue(all(len(n['children']) != 1 for n in tree['nodes']))
                self.assertNotEqual(len(tree['root_children']), 1)
        menu = tree_of(MENU)  # Box { … } is the only statement besides close(); the root keeps both
        self.assertEqual(len(menu['root_children']), 2)

    def test_bodyless_signatures_of_one_kind_merge(self):
        tree = tree_of(REPO)
        self.assertEqual(len(tree['root_children']), 2)
        lines = REPO.split('\n')
        self.assertEqual([lines[j].strip() for j in tree['nodes'][tree['root_children'][1]]['lines']],
                         ['fun buy(id: String)', 'fun sell(id: String)'])

    def test_expression_body_has_no_tree(self):
        self.assertIsNone(tree_of('fun f(x: Int) =\n    x + 1\n'))

    def test_scope_list_shows_every_line_once_and_is_deterministic(self):
        for text in all_texts():
            tree = tree_of(text)
            if tree and tree['root_children']:
                listing = s.scope_listing({'id': 'X'}, text, tree)
                self.assertEqual(listing, s.scope_listing({'id': 'X'}, text, tree_of(text)))
                rows = [line for line in listing.split('\n') if '| ' in line[:4] and '⟨#' not in line]
                self.assertEqual(len(rows), len(text.rstrip('\n').split('\n')))


class Scenes(unittest.TestCase):
    def test_every_fixture_and_sample_unfolds_back_to_the_source(self):
        for text in all_texts():
            tree = tree_of(text)
            if tree and tree['root_children']:
                self.assertEqual(scenes_of(text)[2][-1].rstrip('\n'), text.rstrip('\n'))

    def test_outline_shows_every_step_nested_and_folds_unused_parameters(self):
        _, steps, scenes = scenes_of(NESTED)
        outline = scenes[0]
        marks = [line for line in outline.split('\n') if line.strip().startswith('⟨')]
        self.assertEqual([int(re.search(r'⟨(\d+)\.', m).group(1)) for m in marks], list(range(1, len(steps) + 1)))
        depth = {k + 1: st['depth'] for k, st in enumerate(steps)}
        indent = {int(re.search(r'⟨(\d+)\.', m).group(1)): len(m) - len(m.lstrip()) for m in marks}
        for k in indent:
            self.assertEqual(indent[k] - indent[1], 4 * depth[k])
        self.assertIn('    ...\n', outline)
        self.assertNotIn('Basic(', outline)

    def test_one_layer_per_scene(self):
        for text in [NESTED, SHOP, MENU, VM]:
            _, steps, scenes = scenes_of(text)
            for k, scene in enumerate(scenes):
                left = {int(n) for n in re.findall(r'⟨(\d+)\. ', scene)}
                self.assertEqual(left, set(range(k + 1, len(steps) + 1)), (text[:20], k))

    def test_no_blank_left_above_a_closing_line_by_hidden_members(self):
        text = 'class T {\n    fun a() {\n        x()\n        y(h)\n    }\n\n    private val h = 1\n}\n'
        _, _, scenes = scenes_of(text)
        self.assertTrue(scenes[0].endswith('    }\n}\n'), scenes[0])
        self.assertEqual(scenes[-1], text)

    def test_attached_state_and_parameters_appear_where_first_used(self):
        _, steps, scenes = scenes_of(NESTED)
        first = next(k for k, sc in enumerate(scenes) if 'var layout' in sc)
        self.assertIn('layout = result', scenes[first])
        self.assertNotIn('var layout', scenes[first - 1])
        self.assertIn('    style: Style = Style(),', scenes[1])  # used by the first step
        self.assertNotIn('onLayout: (', scenes[1])

    def test_only_one_line_members_attach_and_multiline_ones_unfold_in_layers(self):
        for text in all_texts():
            tree = tree_of(text)
            if tree:
                lines = text.split('\n')
                for a in tree['attached']:
                    code = [j for j in a['lines'] if not s.COMMENT_LINE.match(lines[j]) and not s.ANNOTATION_LINE.match(lines[j])]
                    self.assertEqual(len(code), 1, (text[:20], a['name']))
        tree, steps, scenes = scenes_of(VM)
        self.assertEqual([a['name'] for a in tree['attached']], ['selected'])  # constructor properties stay in the head
        lines = VM.split('\n')
        items = next(n for n in tree['root_children'] 
                     if any('private val items' in lines[j] for j in tree['nodes'][n]['lines']))
        self.assertTrue(tree['nodes'][items]['children'])
        self.assertIn('// the items of the selected id', scenes[1])
        self.assertIn('private val items', scenes[1])
        self.assertNotIn('flowOf', scenes[1])  # the inner layers stay for later steps
        self.assertIn('private val selected', scenes[1])  # first used by items
        self.assertNotIn('private val selected', scenes[0])
        self.assertEqual(scenes[-1], VM)

    def test_one_group_in_two_places_shares_number_and_sentence(self):
        tree = tree_of(NESTED)
        entry = auto_entry(tree)
        basic = s.tree_scopes(tree).index(tree['root_children'][1])
        entry[basic] = {'s': '필드를 띄운다.', 'sep': [{'ids': [1, 3], 's': '바깥에서 받은 값을 넘긴다.'}, {'ids': [2]}]}
        _, _, scenes = scenes_of(NESTED, entry)
        self.assertEqual(scenes[2].count('⟨3. 바깥에서 받은 값을 넘긴다.⟩'), 2)
        self.assertIn('state = state,', scenes[3])
        self.assertIn('decorator = { inner ->', scenes[3])


class Outline(unittest.TestCase):
    def check(self, text, entry, band='필드를 그린다.'):
        return s.check_outline({'id': 'X', 'responsibility': band}, tree_of(text), entry)

    def test_rejections_name_every_bad_scope_at_once(self):
        tree = tree_of(NESTED)
        good = auto_entry(tree)
        self.assertEqual(self.check(NESTED, good)[0], [])
        cases = [
            ('s', 'A를 구하고, B를 그린다.'), ('s', '값을 구하고 그린다.'), ('s', '가' * 46), ('s', '⟨x⟩를 한다.'),
            ('s', '필드를 그린다'), ('s', ''), ('with', [1]), ('sep', [{'ids': [1]}]), ('sep', [{'ids': [1, 1, 2]}]),
            ('sep', [{'ids': ['1']}]), ('sep', [{'ids': [1, 2]}]),
        ]
        for key, value in cases:
            bad = json.loads(json.dumps(good))
            bad[0][key] = value
            errors = self.check(NESTED, bad)[0]
            self.assertEqual(len(errors), 1, (key, value, errors))
            self.assertTrue(errors[0].startswith('X 스코프 #1: '), errors)
        root = json.loads(json.dumps(good))
        root[-1]['s'] = '루트에 쓴 문장이다.'
        root[0]['s'] = ''
        self.assertEqual(len(self.check(NESTED, root)[0]), 2)
        self.assertTrue(self.check(NESTED, good[:-1])[0])
        five = auto_entry(tree_of(FIVE))
        five[-1] = {'sep': [{'ids': [i], 's': '할 일을 마친다.'} for i in range(1, 6)]}
        self.assertIn('4개를 넘음', self.check(FIVE, five)[0][0])


class Workflow(unittest.TestCase):
    def prepare(self, root, view_name, work_name, **extra):
        shutil.copytree(FIXTURE / 'src', root / 'src')
        view = root / view_name
        shutil.copyfile(FIXTURE / view_name, view)
        meta, listing = run(s.cmd_prepare, view=str(view), show=extra.get('show'), hide=extra.get('hide'),
                            output_dir=None, pick=extra.get('pick'))
        result = Path(meta['dir'])
        if work_name:
            shutil.copytree(FIXTURE / work_name / '01', result / 'work/01')
            shutil.copyfile(FIXTURE / work_name / 'outline.json', result / 'work/outline.json')
        return view, meta, listing, result

    def test_fixture_documents_and_inputs_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            view, meta, listing, result = self.prepare(root, 'view.architecture.md', 'unfold')
            before = {p: p.read_bytes() for p in list((root / 'src').iterdir()) + [view]}
            for expected in (FIXTURE / 'expected/original').glob('*.kt'):
                actual = result / 'work/original' / expected.name
                if actual.exists():
                    self.assertEqual(actual.read_bytes(), expected.read_bytes())
            self.assertIn('===== OrderService · 책임: 주문을 받아 처리한다. · 스코프 2개 =====', listing)
            self.assertIn(' 1|         require(', listing)
            self.assertNotIn('===== Validator', listing)  # one statement inside one member: nothing to unfold
            prompt = Path(meta['stage1_prompt']).read_text(encoding='utf-8')
            self.assertFalse(any(line.strip().startswith('click ') for line in prompt.split('\n')))
            self.assertIn('#### 요소의 책임', prompt)
            built, _ = run(s.cmd_build, dir=str(result))
            self.assertEqual(built['verified'], 4)
            self.assertEqual(len(built['skipped']), 3)
            first = {doc: Path(doc).read_bytes() for doc in built['docs']}
            run(s.cmd_build, dir=str(result))
            self.assertEqual({doc: Path(doc).read_bytes() for doc in built['docs']}, first)  # same input, same documents
            manifest = s.load_manifest(result)
            base, _, _ = s.build_documents(result, manifest, parsed_outline(result, manifest), with_diff=False)
            for doc in built['docs']:
                actual = Path(doc)
                expected = FIXTURE / 'expected' / actual.name
                if os.environ.get('REGENERATE'):
                    expected.write_bytes(actual.read_bytes())
                    expected.with_suffix('.base.md').write_text(base[actual.name], encoding='utf-8', newline='\n')
                self.assertEqual(actual.read_bytes(), expected.read_bytes())
                self.assertEqual(s.strip_diff_layer(actual.read_text(encoding='utf-8')),
                                 expected.with_suffix('.base.md').read_text(encoding='utf-8'))
            text = (result / 'OrderDomain.md').read_text(encoding='utf-8')
            self.assertIn('<div class="resp"><span class="label">책임</span> 주문을 받아 처리한다.</div>', text)
            self.assertIn('3단계: 펼치기 1/4 — 주문 하나를 처리해 영수증을 돌려준다. (3/6)', text)
            self.assertIn('⟨3. 처리한 주문을 감사 기록에 남긴다.⟩', text)
            self.assertNotIn('단계: 원본', text.split('### Validator')[0])  # OrderService: the last unfold is the source
            self.assertIn('2단계: 원본 (2/2)', text.split('### Validator')[1])  # nothing to unfold: situation, then source
            self.assertEqual({p: p.read_bytes() for p in before}, before)
            (root / 'src/Order.kt').write_text((root / 'src/Order.kt').read_text(encoding='utf-8').replace('reserve(order.id)', 'reserve(order.key)'), encoding='utf-8')
            self.assertEqual(exit_code(['build', str(result)]), 3)

    def test_source_less_node_shows_only_the_situation(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, _, result = self.prepare(Path(tmp), 'view.architecture.md', 'unfold')
            manifest = s.load_manifest(result)
            node = next(n for n in manifest['nodes'] if n['id'] == 'PaymentGateway')
            scenes = s.node_scenes(result, manifest, node, {})
            self.assertEqual([kind for _, kind, _ in scenes], ['prose'])

    def test_depth_one_node_unfolds_its_groups_without_a_source_scene(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, _, result = self.prepare(Path(tmp), 'view.architecture.md', 'unfold')
            manifest = s.load_manifest(result)
            node = next(n for n in manifest['nodes'] if n['id'] == 'InventoryRepository')
            tree = node['tree']
            self.assertTrue(all(not tree['nodes'][c]['children'] for c in tree['root_children']))  # depth 1
            scenes = s.node_scenes(result, manifest, node, parsed_outline(result, manifest))
            self.assertEqual([name.split(' ')[0] for name, _, _ in scenes], ['사용', '윤곽', '펼치기', '펼치기'])
            self.assertEqual(scenes[-1][2].rstrip('\n'), (result / 'work/original/InventoryRepository.kt').read_text(encoding='utf-8').rstrip('\n'))

    def test_hidden_unfold_goes_from_outline_to_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, _, result = self.prepare(Path(tmp), 'view.architecture.md', 'unfold', hide='펼치기')
            manifest = s.load_manifest(result)
            node = next(n for n in manifest['nodes'] if n['id'] == 'OrderService')
            self.assertEqual([name for name, _, _ in s.node_scenes(result, manifest, node, parsed_outline(result, manifest))],
                             ['사용 상황', '윤곽', '원본'])

    def test_bad_outline_and_missing_files_exit_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, _, result = self.prepare(Path(tmp), 'view.architecture.md', 'unfold')
            good = (result / 'work/outline.json').read_text(encoding='utf-8')
            bad = good.replace('"s": "주문 하나를 처리해 영수증을 돌려준다."', '"s": "주문을 받고, 처리한다."').replace('"ids": [3]', '"ids": [9]')
            (result / 'work/outline.json').write_text(bad, encoding='utf-8')
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as failed:
                s.main(['build', str(result)])
            self.assertEqual(failed.exception.code, 2)
            self.assertEqual([line.split(':')[0] for line in err.getvalue().strip().splitlines()],
                             ['OrderService 스코프 #1', 'InventoryRepository 스코프 #1'])  # every bad scope, one line each
            (result / 'work/outline.json').write_text(good, encoding='utf-8')
            run(s.cmd_build, dir=str(result))
            (result / 'work/outline.json').unlink()
            self.assertEqual(exit_code(['build', str(result)]), 2)
            self.assertEqual(exit_code(['begin', str(result), '2']), 2)

    def test_overload_pick(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            meta, listing = self.prepare(root, 'overload.architecture.md', None)[1:3]
            self.assertEqual(len(meta['pick'][0]['candidates']), 2)
            self.assertEqual(listing, '')
            shutil.rmtree(root / 'src')
            _, meta, listing, result = self.prepare(root, 'overload.architecture.md', 'unfold-overload', pick='Screen:1')
            self.assertEqual((result / 'work/original/Screen.kt').read_bytes(),
                             (FIXTURE / 'expected/original/overload-Screen.kt').read_bytes())
            built, _ = run(s.cmd_build, dir=str(result))
            self.assertEqual(built['verified'], 1)


LANG_VIEW = '''### Dependency

```mermaid
flowchart LR
  ColorsXml@{ label: "colors.xml" }
  ColorKt@{ label: "Color.kt" }
  Circle
  Order

  click ColorsXml "res/colors.xml" "colors.xml"
  click ColorKt "src/Color.kt" "Color.kt"
  click Circle "src/Shapes.java" "Shapes.java"
  click Order "src/Order.kt" "Order.kt"
```
'''
LANG_SOURCES = {
    'res/colors.xml': '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="black">#FF000000</color>\n</resources>\n',
    'src/Color.kt': ('package demo.ui\n\nimport androidx.compose.ui.graphics.Color\n\n/** Brand blue. */\n'
                     'val Blue = Color(0xFF0000FF)\nval Red = Color(0xFFFF0000)\nval Green = Color(0xFF00FF00)\n'),
    'src/Shapes.java': 'class Circle {\n}\n\nclass Square {\n}\n',
    'src/Order.kt': 'package demo\n\nclass Order {\n    fun a() {\n        x()\n    }\n\n    fun b() = 1\n}\n',
}


class Languages(unittest.TestCase):
    """Sources in any language and nodes that name their file (spec FR-002, FR-017, FR-017a, SC-013)."""

    def test_file_level_nodes_and_sources_that_are_not_kotlin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel_path, text in LANG_SOURCES.items():
                (root / rel_path).parent.mkdir(parents=True, exist_ok=True)
                (root / rel_path).write_text(text, encoding='utf-8', newline='\n')
            view = root / 'lang.architecture.md'
            view.write_text(LANG_VIEW, encoding='utf-8', newline='\n')
            meta, listing = run(s.cmd_prepare, view=str(view), show=None, hide=None, output_dir=None, pick=None)
            result = Path(meta['dir'])
            manifest = s.load_manifest(result)
            nodes = {n['id']: n for n in manifest['nodes']}

            xml = nodes['ColorsXml']
            self.assertIsNone(xml['skip_reason'])
            self.assertTrue(xml['range']['whole_file'])
            self.assertIsNone(xml['tree'])

            color = nodes['ColorKt']
            self.assertIsNone(color['skip_reason'])
            self.assertTrue(color['range']['whole_file'])
            self.assertEqual(len(color['tree']['root_children']), 3)  # Blue (with its comment), Red, Green
            self.assertIn(' -| package demo.ui', listing)
            self.assertIn(' -| import androidx.compose.ui.graphics.Color', listing)
            self.assertIn(' 1| /** Brand blue. */', listing)

            self.assertEqual(nodes['Circle']['skip_reason'],
                             'Kotlin이 아닌 원본은 파일 단위 노드만 원본 범위를 정할 수 있어 구체화하지 않음')
            self.assertNotIn('whole_file', nodes['Order']['range'])  # the declaration comes first
            self.assertEqual(nodes['Order']['range']['start_line'], 3)

            (result / 'work/01').mkdir(parents=True)
            for n in manifest['nodes']:
                (result / 'work/01' / (n['id'] + '.kt')).write_text('필요한 사람이 쓴다.', encoding='utf-8')
            outline = {n['id']: auto_entry(n['tree']) for n in manifest['nodes'] if n['tree'] and n['tree']['root_children']}
            (result / 'work/outline.json').write_text(json.dumps(outline, ensure_ascii=False), encoding='utf-8')
            built, _ = run(s.cmd_build, dir=str(result))
            self.assertEqual(built['verified'], 3)
            self.assertEqual([x['node'] for x in built['skipped']], ['Circle'])
            doc = Path(built['docs'][0]).read_text(encoding='utf-8')
            self.assertNotIn('⚠️', doc.split('### Circle')[0])

            box = doc.split('### colors.xml')[1].split('### ')[0]
            self.assertIn('2단계: 원본 (2/2)', box)
            self.assertIn('```xml\n' + LANG_SOURCES['res/colors.xml'], box)

            scenes = s.node_scenes(result, manifest, color, parsed_outline(result, manifest))
            self.assertIn('package demo.ui', scenes[1][2])  # the outline shows the file header
            self.assertEqual(scenes[-1][2].rstrip('\n'), LANG_SOURCES['src/Color.kt'].rstrip('\n'))


class Render(unittest.TestCase):
    def test_prose_is_escaped_not_syntax_highlighted(self):
        box = s.render_box('A', [('Situation', '', '<script>x</script> & text'), ('Code', '', 'class A')], [None, None], ['prose', 'code'])
        first, second = box.split('<div class="stage s2">')
        self.assertNotIn('```', first)
        self.assertIn('&lt;script&gt;', first)
        self.assertIn('```kotlin', second)


if __name__ == '__main__':
    unittest.main()
