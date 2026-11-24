"""Run from the repository root: python specs/010-stepwise-code-convergence/test_learning_stages.py.

Set REGENERATE=1 to rewrite fixtures/expected/*.md from the current output (then review the diff).
"""
import contextlib
import html
import importlib.util
import io
import json
import os
import re
from pathlib import Path
import shutil
import tempfile
import urllib.parse
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
        self.assertEqual([x['kind'] for x in stages], list(s.KINDS) + [s.CHANGE, s.BEFORE])
        self.assertEqual([x['nickname'] for x in stages], ['사용 상황', '윤곽', '펼치기', '원본', '변화', '변경 전'])

    def test_hiding_and_unknown_names(self):
        planned, notices = s.plan_stages(s.parse_stage_definition(), {'윤곽': False, '없는 단계': True}, [], ['펼치기', '원본'])
        self.assertEqual([x['visible'] for x in planned], [True, False, False, True, True, True])
        self.assertEqual(len(notices), 2)

    def test_change_stage_is_optional_and_not_toggled(self):
        planned, notices = s.plan_stages(s.parse_stage_definition(), {'변화': False, '변경 전': False}, ['변화'], ['변경 전'])
        self.assertEqual([x['kind'] for x in planned[-2:]], ['change', 'before'])
        self.assertTrue(all(x['visible'] for x in planned[-2:]))
        self.assertEqual(len(notices), 4)  # settings (two), --show, --hide: each ignored with one line
        with tempfile.TemporaryDirectory() as tmp:
            four = Path(tmp) / 'stages.md'
            text = s.read_text(s.STAGES_FILE)
            four.write_text(text[:text.index('## 변화')], encoding='utf-8')
            self.assertEqual([x['kind'] for x in s.parse_stage_definition(four)], list(s.KINDS))
            alone = Path(tmp) / 'alone.md'
            alone.write_text(text[:text.index('## 변화')] + text[text.index('## 변경 전'):], encoding='utf-8')
            with self.assertRaises(s.InputError):  # stage -1 only with stage 0 (FR-034)
                s.parse_stage_definition(alone)

    def test_node_display_marks_are_not_part_of_the_source_name(self):
        cases = {
            'class&nbsp;NiaAppState': 'NiaAppState',
            'enum&nbsp;class&nbsp;TopLevelDestination': 'TopLevelDestination',
            '♻️&nbsp;fun&nbsp;NiaNavHost()': 'NiaNavHost',
            'render()': 'render',
            'PlainNode': 'PlainNode',
            "<a href='../app/NiaApp.kt'>♻️&nbsp;<b>fun&nbsp;NiaApp()</b></a>": 'NiaApp',  # linked label (architecture view)
        }
        self.assertEqual({label: s.clean_name(label) for label in cases}, cases)


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

    def test_expression_bodies_continue_past_comment_and_blank_lines(self):
        text = '''fun Modifier.a(): Modifier =
    // comment
    zIndex(1f)
        // comment
        .graphicsLayer { translationY = 0f }

fun <T> List<T>.b(): List<T> =
    /* block
       comment */
    toMutableList()

val c =

    42
'''
        self.assertEqual(s.find_declaration(text, ['a'])[0], (1, 5))
        self.assertEqual(s.find_declaration(text, ['b'])[0], (7, 10))
        self.assertEqual(s.find_declaration(text, ['c'])[0], (12, 14))


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
            ('s', '필드를 그린다'), ('s', '재고 확인'), ('s', ''), ('with', [1]), ('sep', [{'ids': [1]}]), ('sep', [{'ids': [1, 1, 2]}]),
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
            self.assertEqual(built['verified'], 5)  # LegacyBridge (Java) has a range too since research S11
            self.assertEqual(len(built['skipped']), 2)
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
            self.assertEqual(text.count('<details class="zenuml-stepwise-style">'), 1)
            self.assertEqual(text.count('<style>'), 2)
            self.assertIn('관련 GFM 공식 문서</a>)</summary>', text)
            self.assertIn('.zenuml-stepwise-style { display: none; }', text)
            self.assertIn('<div class="resp"><span class="label">책임</span> 주문을 받아 처리한다.</div>', text)
            self.assertIn('3/6단계: 펼치기 — 1. 주문 하나를 처리해 영수증을 돌려준다.</span>', text)
            unfolds = re.findall(r'단계: 펼치기 — (\d+)\. (.+?)</span>', text)
            self.assertTrue(unfolds)
            for number, title in unfolds:  # the title carries its placeholder's number (FR-039)
                self.assertIn('⟨%s. %s⟩' % (number, title), text)
            self.assertIn('⟨3. 처리한 주문을 감사 기록에 남긴다.⟩', text)
            self.assertNotIn('단계: 원본', text.split('**Validator**')[0])  # OrderService: the last unfold is the source
            self.assertIn('2/2단계: 원본</span>', text.split('**Validator**')[1])  # nothing to unfold: situation, then source
            self.assertEqual({p: p.read_bytes() for p in before}, before)
            (root / 'src/Order.kt').write_text((root / 'src/Order.kt').read_text(encoding='utf-8').replace('reserve(order.id)', 'reserve(order.key)'), encoding='utf-8')
            self.assertEqual(exit_code(['build', str(result)]), 3)

    def test_stages_share_one_scroll_box_and_keep_their_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, _, result = self.prepare(Path(tmp), 'view.architecture.md', 'unfold')
            built, _ = run(s.cmd_build, dir=str(result))
            manifest = s.load_manifest(result)
            parsed = parsed_outline(result, manifest)
            doc = '\n'.join(Path(d).read_text(encoding='utf-8') for d in built['docs'])
            for node in manifest['nodes']:
                scenes = s.node_scenes(result, manifest, node, parsed)
                box = doc[doc.index('<input type="radio" name="%s"' % node['id']):]
                box = re.split(r'\n### |\n<details', box)[0]  # up to the next node or the style block
                with self.subTest(node['id']):
                    self.assertEqual(box.count('<div class="scroller">'), 1)
                    self.assertEqual(box.count('<div class="pane p'), len(scenes))
                    self.assertLess(box.rindex('<div class="stage s'), box.index('<div class="scroller">'))  # headings above
                    fences = re.findall(r'\n(`{3,})[\w+.#-]*\n(.*?)\n\1\n', box[box.index('<div class="scroller">'):], re.S)
                    self.assertEqual([code for _, code in fences], [c.rstrip('\n') for _, kind, c in scenes if kind == 'code'])
            self.assertIn('.stages > .scroller { max-height: min(30lh, 70vh); overflow: auto;', doc)
            self.assertNotIn('.stages .code { max-height', doc)

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

    def test_hidden_situation_needs_no_stage1_files(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            _, with_files, _, ra = self.prepare(Path(a), 'view.architecture.md', 'unfold', hide='사용 상황')
            _, meta, _, rb = self.prepare(Path(b), 'view.architecture.md', None, hide='사용 상황')
            shutil.copyfile(FIXTURE / 'unfold/outline.json', rb / 'work/outline.json')
            self.assertIsNone(meta['stage1_prompt'])
            self.assertFalse((rb / 'work/stage1-prompt.md').exists())
            built_a, _ = run(s.cmd_build, dir=str(ra))
            built_b, _ = run(s.cmd_build, dir=str(rb))
            self.assertEqual([Path(d).read_bytes() for d in built_a['docs']], [Path(d).read_bytes() for d in built_b['docs']])

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

            self.assertIsNone(nodes['Circle']['skip_reason'])  # Java declarations are found (research S11)
            self.assertEqual((nodes['Circle']['range']['start_line'], nodes['Circle']['range']['end_line']), (1, 2))
            self.assertNotIn('whole_file', nodes['Order']['range'])  # the declaration comes first
            self.assertEqual(nodes['Order']['range']['start_line'], 3)

            (result / 'work/01').mkdir(parents=True)
            for n in manifest['nodes']:
                (result / 'work/01' / (n['id'] + '.kt')).write_text('필요한 사람이 쓴다.', encoding='utf-8')
            outline = {n['id']: auto_entry(n['tree']) for n in manifest['nodes'] if n['tree'] and n['tree']['root_children']}
            (result / 'work/outline.json').write_text(json.dumps(outline, ensure_ascii=False), encoding='utf-8')
            built, _ = run(s.cmd_build, dir=str(result))
            self.assertEqual(built['verified'], 4)
            self.assertEqual(built['skipped'], [])
            doc = Path(built['docs'][0]).read_text(encoding='utf-8')
            self.assertNotIn('⚠️', doc)
            self.assertIn('```java\nclass Circle {\n}\n```', doc)

            box = doc.split('**colors.xml**')[1].split('### ')[0]
            self.assertIn('2/2단계: 원본</span>', box)
            self.assertIn('```xml\n' + LANG_SOURCES['res/colors.xml'], box)

            scenes = s.node_scenes(result, manifest, color, parsed_outline(result, manifest))
            self.assertIn('package demo.ui', scenes[1][2])  # the outline shows the file header
            self.assertEqual(scenes[-1][2].rstrip('\n'), LANG_SOURCES['src/Color.kt'].rstrip('\n'))


SOURCES_BY_LANGUAGE = {
    'java': ('OrderService', 5, 18, True, """package demo;

import java.util.List;

/** Orders. */
public class OrderService {
    private final Repo repo;

    public OrderService(Repo repo) {
        this.repo = repo;
    }

    public void place(Order order) {
        if (order.ok()) {
            repo.save(order);
        }
    }
}

class Helper {
    void run() {}
}
"""),
    'ts': ('Cart', 3, 13, True, """import { Repo } from "./repo";

export class Cart {
  private items: string[] = [];

  add(id: string): void {
    this.items.push(`${id}}`);
  }

  clear(): void {
    this.items = [];
  }
}

export function total(cart: Cart): number {
  return cart.size();
}
"""),
    'js': ('Store', 7, 15, True, """const api = {
  get(id) {
    return fetch(id);
  },
};

class Store {
  constructor(api) {
    this.api = api;
  }

  load(id) {
    return this.api.get(id) || '}';
  }
}
"""),
    'go': ('Add', 11, 16, True, """package shop

import (
\t"fmt"
)

type Repo struct {
\titems []string
}

func (r *Repo) Add(id string) {
\tif id != "" {
\t\tr.items = append(r.items, id)
\t}
\tfmt.Println(`}`)
}
"""),
    'rs': ('helper', 14, 18, True, """use std::fmt;

#[derive(Debug)]
pub struct Point {
    x: i32,
}

impl Point {
    pub fn new(x: i32) -> Self {
        Point { x }
    }
}

fn helper<'a>(s: &'a str) -> &'a str {
    let c = '}';
    if s.is_empty() { return s; }
    s
}
"""),
    'cs': ('Basket', 5, 14, True, """using System;

namespace Shop;

[Serializable]
public class Basket
{
    private readonly string path = @"C:\\data\\";

    public void Add(string id)
    {
        Console.WriteLine(id);
    }
}
"""),
    'swift': ('Counter', 3, 13, True, """import Foundation

final class Counter {
    private var count = 0

    func increment() {
        count += 1
    }

    func reset() {
        count = 0
    }
}

extension Counter {
    func log() {}
}
"""),
    'cpp': ('Stack', 3, 11, True, """#include <vector>

template <typename T>
class Stack {
public:
    void push(T v) {
        items.push_back(v);
    }
private:
    std::vector<T> items;
};

int size() { return 0; }
"""),
    'py': ('Store', 5, 17, True, 'import os\nfrom typing import List\n\n\n@dataclass\nclass Store:\n'
           '    """Keeps items: {"a": 1}."""\n\n    def __init__(self, root):\n        self.root = root\n\n'
           '    def load(self, name):\n        path = os.path.join(self.root, name)\n'
           '        if os.path.exists(path):\n            return open(path).read()\n        else:\n'
           '            return None\n\n\ndef helper():\n    return 1\n'),
    'scala': ('Cart', 3, 11, True, """import scala.collection.mutable

class Cart(repo: Repo) {
  private val items = mutable.Buffer[String]()

  def add(id: String): Unit = {
    items += s"${id}}"
  }

  def clear(): Unit = items.clear()
}

object CartOps
"""),
    'groovy': ('Builder', 3, 11, True, """import groovy.transform.CompileStatic

class Builder {
    def steps = []

    void step(String name) {
        steps << "${name}}"
    }

    def run() { steps.each { println it } }
}
"""),
    'dart': ('Counter', 3, 13, True, """import 'package:flutter/material.dart';

class Counter {
  int _count = 0;

  void increment() {
    _count++;
  }

  void reset() {
    _count = 0;
  }
}
"""),
    'c': ('add_item', 9, 14, True, """#include <stdio.h>

struct Cart {
    int count;
};

static int helper(void);

int add_item(struct Cart *cart, const char *id)
{
    if (id[0] == '}') return 0;
    cart->count++;
    return cart->count;
}
"""),
}


def unfold_all(code, lang):
    """Every scene of a range with an outline that keeps each child apart; the last must be the range."""
    tree = s.build_tree(code, lang=lang)
    if tree is None or not tree['root_children']:
        return tree, None
    errors, parsed = s.check_outline({'id': 'X'}, tree, auto_entry(tree))
    assert not errors, errors
    steps = s.plan_steps(tree, parsed)
    lines = code.rstrip('\n').split('\n')
    at = s.attach_steps(tree, steps, lines, s.mask_code(code, lang).rstrip('\n').split('\n'))
    return tree, s.render_steps_scene(tree, lines, steps, at, len(steps))


class OtherLanguages(unittest.TestCase):
    """Languages whose block structure the scanner knows (spec FR-002, FR-017a, SC-014, research S11)."""

    def test_declarations_are_cut_and_unfold_back_to_the_range(self):
        for ext, (name, first, last, nested, text) in SOURCES_BY_LANGUAGE.items():
            with self.subTest(ext):
                lang = s.LANG_BY_EXT[ext]
                span, reason, candidates = s.find_declaration(text, [name], None, lang)
                self.assertEqual((span, reason, candidates), ((first, last), None, []))
                code = '\n'.join(text.split('\n')[first - 1:last])
                tree, unfolded = unfold_all(code, lang)
                self.assertEqual(bool(tree and tree['root_children']), nested)
                if unfolded is not None:
                    self.assertEqual(unfolded.rstrip('\n'), code.rstrip('\n'))

    def test_python_blocks_follow_indentation(self):
        lang = s.LANG_BY_EXT['py']
        text = SOURCES_BY_LANGUAGE['py'][4]
        code = '\n'.join(text.split('\n')[4:17])
        tree = s.build_tree(code, lang=lang)
        kids = [tree['nodes'][c] for c in tree['root_children']]
        self.assertEqual(len(kids), 3)  # docstring, __init__, load
        load = kids[2]
        self.assertTrue(load['children'])  # its body is a scope
        self.assertEqual(tree['attached'], [])  # __init__ is not private: dunder names are public

    def test_file_level_nodes_outside_kotlin_keep_the_head_in_the_root(self):
        cases = {
            'java': 'package demo;\n\nimport java.util.List;\n\nclass A {\n    void f() {}\n}\n\nclass B {\n    void g() {}\n}\n',
            'py': 'import os\nfrom typing import List\n\n\ndef a():\n    return 1\n\n\ndef b():\n    return 2\n',
        }
        for ext, text in cases.items():
            with self.subTest(ext):
                lang = s.LANG_BY_EXT[ext]
                tree = s.build_tree(text, whole_file=True, lang=lang)
                lines = text.rstrip('\n').split('\n')
                head = [j for j, line in enumerate(lines) if line.startswith(('package', 'import', 'from'))]
                self.assertTrue(set(head) <= set(tree['root']))
                self.assertEqual(len(tree['root_children']), 2)
                errors, parsed = s.check_outline({'id': 'X'}, tree, auto_entry(tree))
                self.assertEqual(errors, [])
                steps = s.plan_steps(tree, parsed)
                at = s.attach_steps(tree, steps, lines, s.mask_code(text, lang).rstrip('\n').split('\n'))
                self.assertEqual(s.render_steps_scene(tree, lines, steps, at, len(steps)).rstrip('\n'), text.rstrip('\n'))
                self.assertIn(lines[0], s.render_steps_scene(tree, lines, steps, at, 0))  # the outline shows the head

    def test_regex_literals_are_masked(self):
        text = 'function parse(text) {\n  const re = /}"/;\n  return re.test(text);\n}\n'
        self.assertEqual(s.find_declaration(text, ['parse'], None, s.LANG_BY_EXT['js'])[0], (1, 4))

    def test_a_range_the_block_structure_does_not_confirm_is_not_used(self):
        # a regex right after `)` reads as division to the scanner, so its `}` closes the body early
        text = 'function parse(text, ok) {\n  if (ok) /}/.test(text);\n  return text;\n}\n'
        span, reason, _ = s.find_declaration(text, ['parse'], None, s.LANG_BY_EXT['js'])
        self.assertIsNone(span)
        self.assertEqual(reason, '원본 파일에서 parse 선언 범위를 블록 구조로 확인하지 못해 구체화하지 않음')

    def test_calls_and_constructors_are_not_separate_declarations(self):
        lang = s.LANG_BY_EXT['java']
        text = SOURCES_BY_LANGUAGE['java'][4]
        self.assertEqual(s.find_declaration(text, ['place'], None, lang)[0], (13, 17))
        self.assertEqual(s.find_declaration(text + 'class X { void f() { place(o); } }\n', ['place'], None, lang)[0], (13, 17))


BEFORE_MISSING = '''package com.shop.pay

class PaymentGateway {
    fun charge(id: String) {
        log(id)
        send(id)
    }
}

class SomethingElse
'''


def git(root, *argv):
    import subprocess
    subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'core.autocrlf=false', *argv],
                   cwd=root, check=True, capture_output=True)


def stage0_rows(doc, node_id):
    """(line, class) rows of a node's stage 0, read back from its diff layer."""
    box = doc[doc.index('id="%s-0"' % node_id):]
    slide = box[box.index('<div class="pane p0">'):box.index('<div class="pane p1">')]
    layer = slide[slide.index('<pre class="diff"'):slide.index('</pre>')]
    return [(html.unescape(text), cls or None) for cls, text in re.findall(r'<span(?: class="([a-z]+)")?>(.*?)</span>\n', layer)]


@unittest.skipUnless(shutil.which('git'), 'git이 없음')
class ChangeStage(unittest.TestCase):
    """Stage 0 when the request names a comparison point (spec FR-028~032, SC-020, SC-021)."""

    def build(self, root, **extra):
        meta, listing = run(s.cmd_prepare, view=str(root / 'view.architecture.md'), show=None, hide=None,
                            output_dir=None, pick=None, base=extra.get('base'), head=extra.get('head'))
        result = Path(meta['dir'])
        shutil.copytree(FIXTURE / 'unfold/01', result / 'work/01')
        outline = json.loads((FIXTURE / 'unfold/outline.json').read_text(encoding='utf-8'))
        manifest = s.load_manifest(result)
        for node in manifest['nodes']:
            if node['id'] not in outline and node.get('tree') and node['tree']['root_children']:
                outline[node['id']] = auto_entry(node['tree'])
        (result / 'work/outline.json').write_text(json.dumps(outline, ensure_ascii=False), encoding='utf-8')
        built, _ = run(s.cmd_build, dir=str(result))
        return meta, listing, result, built

    def assert_title_links(self, manifest, result, doc):
        """Every node title is its bold name, linked to the view's link as seen from the result folder (FR-037)."""
        view_dir = Path(manifest['view']).parent.resolve()
        for node in manifest['nodes']:
            with self.subTest(title=node['id']):
                m = re.search(r'^### (?:\S+ )?(\[)?\*\*%s\*\*(?:\]\(([^)]*)\))?$' % re.escape(node['name']), doc, re.M)
                self.assertIsNotNone(m)
                if not node['link']:
                    self.assertIsNone(m.group(1))
                    continue
                href = urllib.parse.unquote(m.group(2)).split('#')[0]
                self.assertEqual((result / href).resolve(), (view_dir / node['link'].split('#')[0]).resolve())

    def test_counter_pads_to_the_total_digit_count(self):
        self.assertEqual([s.counter(6, 9), s.counter(6, 12), s.counter(4, 100)], ['6/9', '06/12', '004/100'])

    def test_node_title_escapes_the_name_and_keeps_urls(self):
        url = 'https://example.com/repo/blob/main/a.kt#L3'
        self.assertEqual(s.node_title({'name': '__init__', 'link': None, 'change': 'added'}, Path('.'), Path('.')),
                         r'### ✨ **\_\_init\_\_**')
        self.assertEqual(s.node_title({'name': 'A[1]', 'link': url, 'change': 'same'}, Path('.'), Path('.')),
                         r'### [**A\[1\]**](%s)' % url)
        with tempfile.TemporaryDirectory() as tmp:
            view_dir, result = Path(tmp), Path(tmp) / 'x.stages'
            self.assertEqual(s.node_title({'name': 'B', 'link': '../src/My File(1).kt#L2', 'change': None}, view_dir, result),
                             '### [**B**](../../src/My%20File%281%29.kt#L2)')

    def test_changed_node_gets_stage0_and_removed_node_uses_its_old_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(FIXTURE / 'src', root / 'src')
            shutil.copyfile(FIXTURE / 'view.architecture.md', root / 'view.architecture.md')
            order = (root / 'src/Order.kt').read_text(encoding='utf-8')
            (root / 'src/Order.kt').write_text(order.replace('        reserved += id\n', '        log(id)\n        reserved.add(id)\n'), encoding='utf-8')
            (root / 'src/Missing.kt').write_text(BEFORE_MISSING, encoding='utf-8')
            git(root, 'init', '-q')
            git(root, 'add', '.')
            git(root, 'commit', '-q', '-m', 'before')
            shutil.copyfile(FIXTURE / 'src/Order.kt', root / 'src/Order.kt')
            shutil.copyfile(FIXTURE / 'src/Missing.kt', root / 'src/Missing.kt')
            git(root, 'commit', '-q', '-am', 'after')

            meta, listing, result, built = self.build(root, base='HEAD~1', head='HEAD')
            manifest = s.load_manifest(result)
            change = {n['id']: n['change'] for n in manifest['nodes']}
            self.assertEqual(change['InventoryRepository'], 'changed')
            self.assertEqual(change['PaymentGateway'], 'removed')
            self.assertEqual(change['OrderService'], 'same')
            self.assertEqual(set(manifest['compare']), {'base', 'head'})
            self.assertNotIn('reserved.add(id)', listing)  # the changed node's old code never reaches the model (SC-021)
            self.assertIn('===== PaymentGateway', listing)

            doc = '\n'.join(Path(d).read_text(encoding='utf-8') for d in built['docs'])
            self.assertEqual(doc.count('<div class="stage s0">'), 1)
            # node titles and the legend box (FR-035~037, SC-024)
            self.assertIn('<div class="legend">✨: 추가<br>♻️: 변경<br>🗑️: 삭제<br>비교 기준: <code>%s</code> → <code>%s</code></div>'
                          % (manifest['compare']['base'], manifest['compare']['head']), doc)
            self.assertEqual(doc.count('<div class="legend">'), len(built['docs']))
            heads = {m.group(2): m.group(1) for m in re.finditer(r'^### (\S+ )?\[?\*\*(.+?)\*\*', doc, re.M)}
            self.assertEqual(heads['InventoryRepository'], '♻️ ')
            self.assertEqual(heads['PaymentGateway'], '🗑️ ')
            self.assertIsNone(heads['OrderService'])
            self.assert_title_links(manifest, result, doc)
            rows = stage0_rows(doc, 'InventoryRepository')
            after = (result / 'work/original/InventoryRepository.kt').read_text(encoding='utf-8')
            before = (result / 'work/before/InventoryRepository.kt').read_text(encoding='utf-8')
            self.assertEqual('\n'.join(t for t, c in rows if c != 'del'), after.rstrip('\n'))
            self.assertEqual('\n'.join(t for t, c in rows if c not in ('add', 'mod')), before.rstrip('\n'))
            self.assertEqual({c for _, c in rows} - {None}, {'del', 'mod'})
            removed = (result / 'work/original/PaymentGateway.kt').read_text(encoding='utf-8')
            self.assertIn('class PaymentGateway', removed)
            self.assertNotIn('<label class="nav" for="OrderService-0">', doc)
            # stage -1: the old code as is, only before the changed node's stage 0 (FR-034, SC-023)
            self.assertEqual(doc.count('<div class="stage s-1">'), 1)
            box = doc[doc.index('id="InventoryRepository--1"'):]
            pane = box[box.index('<div class="pane p-1">'):box.index('<div class="pane p0">')]
            self.assertEqual(re.search(r'\n(`{3,})\w*\n(.*?)\n\1\n', pane, re.S).group(2), before.rstrip('\n'))
            self.assertNotIn('<pre class="diff"', pane)
            stage0 = box[box.index('<div class="stage s0">'):box.index('<div class="stage s1">')]
            self.assertIn('<label class="nav" for="InventoryRepository--1">←</label>', stage0)
            self.assertIn('-1단계: 변경 전 (%s)' % manifest['compare']['base'], box)
            for other in ('OrderService', 'PaymentGateway'):
                self.assertNotIn('id="%s--1"' % other, doc)

            with_base = s.load_manifest(result)
            parsed = parsed_outline(result, with_base)
            scenes = {n['id']: s.node_scenes(result, with_base, n, parsed) for n in with_base['nodes'] if n['id'] != 'PaymentGateway'}
            _, _, plain, plain_built = self.build(root)
            without = s.load_manifest(plain)
            self.assertNotIn('compare', without)
            plain_doc = '\n'.join(Path(d).read_text(encoding='utf-8') for d in plain_built['docs'])
            self.assertNotIn('<div class="legend">', plain_doc)
            self.assertNotRegex(plain_doc, r'(?m)^### (✨|♻️|🗑️)')
            self.assert_title_links(without, plain, plain_doc)
            parsed = parsed_outline(plain, without)
            self.assertEqual({n['id']: s.node_scenes(plain, without, n, parsed) for n in without['nodes'] if n['id'] != 'PaymentGateway'}, scenes)

    def test_overloads_only_in_the_old_code_are_picked_too(self):
        screen = (FIXTURE / 'src/Screen.kt').read_text(encoding='utf-8')
        public_only = screen[:screen.index('\n@Composable\nprivate')].replace('vm::refresh)', 'vm::refresh, animate = true)') + '\n'
        for after, expected in ((public_only, 'changed'), (None, 'removed')):
            with self.subTest(expected), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                shutil.copytree(FIXTURE / 'src', root / 'src')
                view = root / 'overload.architecture.md'
                shutil.copyfile(FIXTURE / 'overload.architecture.md', view)
                git(root, 'init', '-q')
                git(root, 'add', '.')
                git(root, 'commit', '-q', '-m', 'before')
                if after is None:
                    (root / 'src/Screen.kt').unlink()
                else:
                    (root / 'src/Screen.kt').write_text(after, encoding='utf-8')
                git(root, 'commit', '-q', '-am', 'after')
                prepare = dict(view=str(view), show=None, hide=None, output_dir=None, base='HEAD~1', head='HEAD')
                meta, listing = run(s.cmd_prepare, pick=None, **prepare)
                self.assertEqual([(p['id'], len(p['candidates']), 'revision' in p) for p in meta['pick']], [('Screen', 2, True)])
                self.assertEqual(listing, '')  # nothing to write before the pick
                meta, _ = run(s.cmd_prepare, pick='Screen:1', **prepare)
                self.assertEqual(meta['pick'], [])
                node = next(n for n in s.load_manifest(Path(meta['dir']))['nodes'] if n['id'] == 'Screen')
                self.assertEqual(node['change'], expected)
                self.assertEqual(node['range']['start_line'], 3)

    def test_unreadable_comparison_point_builds_without_stage0(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(FIXTURE / 'src', root / 'src')
            shutil.copyfile(FIXTURE / 'view.architecture.md', root / 'view.architecture.md')
            meta, _, result, built = self.build(root, base='HEAD~1')  # not a git repository
            self.assertTrue(any(n.startswith('🕘 0단계를 붙이지 못함') for n in s.load_manifest(result)['notices']))
            self.assertNotIn('class="s0"', '\n'.join(Path(d).read_text(encoding='utf-8') for d in built['docs']))


class Render(unittest.TestCase):
    def test_removed_lines_are_not_marked_in_ordinary_stages(self):
        self.assertEqual(s.diff_lines('a\nb\nc\n', 'a\nc\n'), [set(), set()])
        self.assertEqual(s.diff_lines('a\nb\n', 'a\nx\ny\n'), [set(), {'mod'}, {'add'}])
        self.assertNotIn('border-left-color', s.DIFF_CSS)
        self.assertIn('.stages pre.diff .del { background: oklch(0.7 0.15 25 / 10%); box-shadow: inset 4px 0 0 oklch(0.62 0.17 18); }', s.DIFF_CSS)

    def test_prose_is_escaped_not_syntax_highlighted(self):
        box = s.render_box('A', [('Situation', '', '<script>x</script> & text'), ('Code', '', 'class A')], [None, None], ['prose', 'code'])
        first, second = box.split('<div class="pane p2">')
        self.assertNotIn('```', first)
        self.assertIn('&lt;script&gt;', first)
        self.assertIn('```kotlin', second)


if __name__ == '__main__':
    unittest.main()
