"""API 호출 없이 묶음 생성기의 원문 보존 및 스트리밍 상태를 검증한다."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
import time
import unittest

source = Path(__file__).with_name('main5.py').read_text(encoding='utf-8')
tree = ast.parse(source)
# 설치된 UI/API 패키지 없이도 핵심 생성기와 렌더러를 검사한다.
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
             and node.name in ('batch_text', 'receive_text', 'render_answer')]
ns = dict(time=time, BATCH_CHARS=80, BATCH_SECONDS=0.15,
          READING_HEIGHT=360, MODEL='test')
exec(compile(ast.Module(body=functions, type_ignores=[]), 'main5.py', 'exec'), ns)
batch_text = ns['batch_text']


class View:
    def __init__(self):
        self.texts = []
        self.height = None
        self.state = None

    def __enter__(self): return self
    def __exit__(self, *args): return False
    def container(self, **kwargs):
        self.height = kwargs['height']
        return self
    def empty(self): return self
    def status(self, *args, **kwargs): return self
    def info(self, text): pass
    def warning(self, text): pass
    def write(self, text): pass
    def markdown(self, text): self.texts.append(text)
    def update(self, **kwargs): self.state = kwargs['state']


class Stream:
    def __init__(self, events): self.events = events
    def __enter__(self): return iter(self.events)
    def __exit__(self, *args): return False


class BatchTests(unittest.TestCase):
    def test_first_immediate(self):
        def chunks():
            yield '첫'
            raise AssertionError('첫 표시 전에 다음 조각을 요청했습니다.')
        self.assertEqual(next(batch_text(chunks())), '첫')

    def test_whitespace_and_tail(self):
        chunks = ['# 제목', '\n', '\n- 항목', '\n  - 하위', '\n\n', '끝', ' \n']
        result = list(batch_text(chunks, clock=lambda: 0))
        self.assertEqual(''.join(result), ''.join(chunks))
        self.assertEqual(result[-1], '끝 \n')
        self.assertLess(len(result), len(chunks))

    def test_size_and_paragraph(self):
        self.assertEqual(list(batch_text(['첫', 'ab', 'cd', 'e'], max_chars=4,
                                         clock=lambda: 0)), ['첫', 'abcd', 'e'])
        self.assertEqual(list(batch_text(['첫', '문단\n', '\n', '끝'],
                                         clock=lambda: 0)), ['첫', '문단\n\n', '끝'])

    def test_time_threshold(self):
        times = iter([0, 0, 0.05, 0.16])
        self.assertEqual(list(batch_text(['첫', 'a', 'b'], clock=lambda: next(times))),
                         ['첫', 'ab'])

    def test_empty(self):
        self.assertEqual(list(batch_text(['', ''])), [])

    def test_error_flush(self):
        def chunks():
            yield '첫'
            yield '\n꼬리'
            raise RuntimeError('중단')
        result = batch_text(chunks(), clock=lambda: 0)
        self.assertEqual(next(result), '첫')
        self.assertEqual(next(result), '\n꼬리')
        with self.assertRaisesRegex(RuntimeError, '중단'):
            next(result)

    def test_render_completion_and_failure(self):
        pieces = ['# 일정\n'] + ['- 관광 명소\n'] * 30 + ['마지막 조각 \n']
        for mode in ('success', 'missing', 'failed', 'once'):
            with self.subTest(mode=mode):
                view = View()
                ns['st'] = view
                events = [NS(type='response.output_text.delta', delta=p) for p in pieces]
                if mode in ('success', 'once'):
                    events.append(NS(type='response.completed', response=NS(usage=None)))
                elif mode == 'failed':
                    events.append(NS(type='response.failed'))
                client = NS(responses=NS(create=lambda **kwargs: Stream(events)))
                stats = {}
                if mode == 'success':
                    answer = ns['render_answer'](client, {'input': [], 'instructions': ''}, stats)
                    self.assertEqual(answer, ''.join(pieces))
                    self.assertEqual(view.state, 'complete')
                    self.assertLess(stats['renders'], stats['updates'])
                else:
                    with self.assertRaises(RuntimeError):
                        ns['render_answer'](client, {'input': [], 'instructions': ''}, stats,
                                            fail_once=mode == 'once')
                    self.assertEqual(view.state, 'error')
                self.assertEqual(view.height, "content")
                self.assertEqual(view.texts[-1], stats['partial'])
                self.assertEqual(stats['partial'], pieces[0] if mode == 'once' else ''.join(pieces))


if __name__ == '__main__':
    unittest.main()
