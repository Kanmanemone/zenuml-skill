"""Run from the repository root: python specs/010-stepwise-code-convergence/test_learning_stages.py.

Set REGENERATE=1 to rewrite fixtures/expected/*.md from the current output (then review the diff).
"""
import contextlib
import importlib.util
import io
import json
import os
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


def units_of(text):
    info = s.analyse(text)
    return info, s.make_units(info)


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


class Units(unittest.TestCase):
    def test_attachments_and_cap(self):
        _, units = units_of(SHOP)
        self.assertEqual([s.unit_label(u) for u in units],
                         ['items (+ repo)', 'buy (+ busy, last, clock)', 'a, b', 'c'])

    def test_bodyless_signatures_of_one_kind_merge(self):
        _, units = units_of(REPO)
        self.assertEqual([s.unit_label(u) for u in units], ['items', 'buy, sell'])

    def test_expression_body_has_no_units(self):
        self.assertEqual(units_of('fun f(x: Int) =\n    x + 1\n')[1], [])

    def test_every_fixture_and_sample_unfolds_back_to_the_source(self):
        texts = [SHOP, REPO, MENU] + [p.read_text(encoding='utf-8') for p in (FIXTURE / 'expected/original').glob('*.kt')]
        for text in texts:
            info, units = units_of(text)
            if units:
                full = s.render_scene(info, units, ['x'] * len(units), [], len(units))
                self.assertEqual(full.rstrip('\n'), text.rstrip('\n'))


class Scenes(unittest.TestCase):
    def setUp(self):
        self.info, self.units = units_of(SHOP)
        self.ph = ['목록을 내보낸다', '하나를 사고 기억한다', '보조 일 둘', '보조 일 하나']

    def test_outline_folds_unused_parameters_and_lists_every_job(self):
        outline = s.render_scene(self.info, self.units, self.ph, [], 0)
        self.assertIn(') : Base() {', outline)
        self.assertIn('    ...\n', outline)
        self.assertNotIn('repo', outline)
        self.assertEqual([line.strip() for line in outline.split('\n') if line.strip().startswith('⟨')],
                         ['⟨%s⟩' % p for p in self.ph])

    def test_each_unfold_reveals_exactly_one_more_unit_with_its_comment(self):
        prev = s.render_scene(self.info, self.units, self.ph, [], 0)
        for k in range(1, len(self.units) + 1):
            cur = s.render_scene(self.info, self.units, self.ph, [], k)
            self.assertEqual(prev.count('⟨') - cur.count('⟨'), 1)
            prev = cur
        second = s.render_scene(self.info, self.units, self.ph, [], 2)
        self.assertIn('    /** Buys one item. */\n    fun buy', second)
        self.assertIn('    private val repo: Repo,\n    clock: Clock,', second)

    def test_fold_shows_until_source(self):
        folds = [(10, 10, '처음엔 빈 목록')]
        first = s.render_scene(self.info, self.units, self.ph, folds, 1)
        self.assertIn('            ⟨처음엔 빈 목록⟩\n', first)
        self.assertNotIn('onStart', first)


class Outline(unittest.TestCase):
    def check(self, entry, band='상품을 판다.'):
        info, units = units_of(SHOP)
        return s.check_outline({'id': 'Shop', 'responsibility': band}, units, info, entry)

    def test_rejections(self):
        good = ['가', '나', '다', '라']
        bad = [None, {'placeholders': good[:3]}, {'placeholders': ['', '나', '다', '라']},
               {'placeholders': ['상품을 판다', '나', '다', '라']},
               {'placeholders': good, 'folds': [{'from': 8, 'to': 9, 'text': '첫 줄 포함'}]},
               {'placeholders': good, 'folds': [{'from': 9, 'to': 13, 'text': '두 멤버에 걸침'}]},
               {'placeholders': good, 'folds': [{'from': 9, 'to': 10, 'text': 'a'}, {'from': 10, 'to': 10, 'text': 'b'}]},
               {'placeholders': good, 'folds': [{'from': 10, 'to': 10, 'text': ' '}]}]
        for entry in bad:
            with self.assertRaises(s.InputError, msg=entry):
                self.check(entry)
        self.assertEqual(self.check({'placeholders': good, 'folds': [{'from': 10, 'to': 10, 'text': '접음'}]})[1],
                         [(10, 10, '접음')])


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
            self.assertIn('===== OrderService · 책임: 주문을 받아 처리한다. · 단위 2개 =====', listing)
            self.assertIn(' 10 1|         require(', listing)
            prompt = Path(meta['stage1_prompt']).read_text(encoding='utf-8')
            self.assertFalse(any(line.strip().startswith('click ') for line in prompt.split('\n')))
            self.assertIn('#### 요소의 책임', prompt)
            built, _ = run(s.cmd_build, dir=str(result))
            self.assertEqual(built['verified'], 4)
            self.assertEqual(len(built['skipped']), 3)
            manifest = s.load_manifest(result)
            outline = json.loads((result / 'work/outline.json').read_text(encoding='utf-8'))
            base, _, _ = s.build_documents(result, manifest, outline, with_diff=False)
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
            self.assertIn('펼치기 1/2 — 주문을 확인하고 재고와 결제를 거쳐 영수증을 낸다', text)
            self.assertIn('5단계: 원본 (5/5)', text)  # the fold opens in the source scene
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

    def test_hidden_unfold_goes_from_outline_to_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, _, result = self.prepare(Path(tmp), 'view.architecture.md', 'unfold', hide='펼치기')
            manifest = s.load_manifest(result)
            outline = json.loads((result / 'work/outline.json').read_text(encoding='utf-8'))
            node = next(n for n in manifest['nodes'] if n['id'] == 'OrderService')
            self.assertEqual([name for name, _, _ in s.node_scenes(result, manifest, node, outline)], ['사용 상황', '윤곽', '원본'])

    def test_bad_outline_and_missing_files_exit_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, _, result = self.prepare(Path(tmp), 'view.architecture.md', 'unfold')
            (result / 'work/outline.json').write_text('{"OrderService": {"placeholders": ["하나"]}}', encoding='utf-8')
            self.assertEqual(exit_code(['build', str(result)]), 2)
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


class Render(unittest.TestCase):
    def test_prose_is_escaped_not_syntax_highlighted(self):
        box = s.render_box('A', [('Situation', '', '<script>x</script> & text'), ('Code', '', 'class A')], [None, None], ['prose', 'code'])
        first, second = box.split('<div class="stage s2">')
        self.assertNotIn('```', first)
        self.assertIn('&lt;script&gt;', first)
        self.assertIn('```kotlin', second)


if __name__ == '__main__':
    unittest.main()
