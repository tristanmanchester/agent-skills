"""Execute the real chat template's methods with UI/worker doubles, not Textual.

These regressions test local ownership and decisions. The generated Pilot tests
must still run in a real app environment to validate Textual integration/layout.
"""
import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace
import unittest

TEMPLATE = Path(__file__).parents[1] / 'assets/templates/chat_app.py.tmpl'


class Widget:
    def __init__(self, text='', **kwargs):
        self.message_text = text
        self.markup = kwargs.get('markup', True)
        self.disabled = kwargs.get('disabled', False)
        self.value = ''
        self.children = []
        self.is_vertical_scroll_end = True
        self.scroll_y = 10
        self.is_mounted = True
        self.scrolls = []
    def add_class(self, name):
        self.role = name
    def mount(self, item):
        self.children.append(item)
    def update(self, text):
        self.message_text = text
    def scroll_end(self, **kwargs):
        self.scrolls.append(kwargs)
    def focus(self):
        pass


class App:
    def __init__(self):
        self.nodes = {name: Widget() for name in ('#history', '#prompt', '#send', '#stop', '#reply-status')}
        self.after = []
    def query_one(self, name, _type=None):
        return self.nodes[name]
    def call_after_refresh(self, fn, *args):
        self.after.append((fn, args))


class FakeWorker:
    def __init__(self, fn, args):
        self.fn, self.args, self.cancelled = fn, args, False
    async def run(self):
        return await self.fn(*self.args)
    def cancel(self):
        self.cancelled = True


def work(**options):
    def decorate(fn):
        def start(*args):
            return FakeWorker(fn, args)
        return start
    return decorate


WorkerState = SimpleNamespace(SUCCESS='success', ERROR='error', CANCELLED='cancelled', RUNNING='running')


def load_app():
    text = TEMPLATE.read_text().replace('{{CLASS_NAME}}', 'ChatApp').replace('{{MODULE}}', 'chat_app').replace('{{APP_TITLE}}', 'Chat')
    tree = ast.parse(text)
    tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))
                 or isinstance(node, ast.ImportFrom) and node.module == '__future__']
    scope = dict(__name__='template_under_test', asyncio=asyncio, App=App, ComposeResult=object,
                 Horizontal=Widget, VerticalScroll=Widget, var=lambda value: value,
                 Button=Widget, Footer=Widget, Header=Widget, Input=Widget, Static=Widget,
                 Worker=FakeWorker, WorkerState=WorkerState, work=work)
    exec(compile(tree, str(TEMPLATE), 'exec'), scope)
    return scope['ChatApp'], scope['MessageBubble']


class ChatTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        cls, self.bubble = load_app()
        self.app = cls()
        self.app.on_mount()
    def event(self, worker, state):
        self.app.on_worker_state_changed(SimpleNamespace(worker=worker, state=state))
    async def test_busy_does_not_drop_accepted_prompt_or_draft(self):
        self.assertTrue(self.app.submit_prompt('first'))
        worker = self.app._reply_worker
        self.app.nodes['#prompt'].value = 'second draft'
        self.assertFalse(self.app.submit_prompt('second draft'))
        self.assertIs(self.app._reply_worker, worker)
        self.assertFalse(worker.cancelled)
        self.assertEqual(self.app.nodes['#prompt'].value, 'second draft')
        self.assertEqual(self.app.message_count, 2)
    async def test_success_appends_exact_reply_then_releases_busy(self):
        async def reply(prompt): return 'Reply to ' + prompt
        self.app.build_reply = reply
        self.app.submit_prompt('[bold]literal[/bold]')
        worker = self.app._reply_worker
        await worker.run()
        self.event(worker, WorkerState.SUCCESS)
        self.assertFalse(self.app.busy)
        self.assertEqual(self.app.nodes['#history'].children[-1].message_text, 'Reply to [bold]literal[/bold]')
        self.assertEqual(self.app.reply_status, 'Ready.')
    async def test_display_is_literal_not_markup(self):
        widget = self.bubble('[bold]literal[/bold]', 'user')
        self.assertFalse(widget.markup)
        self.assertEqual(widget.message_text, '[bold]literal[/bold]')
    async def test_failed_reply_has_no_invented_message(self):
        async def fail(prompt): raise RuntimeError('DO NOT DISPLAY SECRET')
        self.app.build_reply = fail
        self.app.submit_prompt('first')
        worker = self.app._reply_worker
        with self.assertRaises(RuntimeError): await worker.run()
        self.event(worker, WorkerState.ERROR)
        self.assertFalse(self.app.busy)
        self.assertEqual(self.app.message_count, 2)
        self.assertNotIn('SECRET', self.app.reply_status)
    async def test_stop_before_start_releases_ownership_immediately(self):
        self.app.submit_prompt('first')
        worker = self.app._reply_worker
        self.app.action_cancel_reply()
        self.assertTrue(worker.cancelled)
        self.assertFalse(self.app.busy)
        self.assertIsNone(self.app._reply_worker)
        self.assertIn('Remote outcome may be unknown', self.app.reply_status)
    async def test_late_reply_and_event_cannot_touch_next_request(self):
        entered, release = asyncio.Event(), asyncio.Event()
        async def reply(prompt):
            if prompt == 'first':
                entered.set()
                await release.wait()
            return 'Reply ' + prompt
        self.app.build_reply = reply
        self.app.submit_prompt('first')
        old = self.app._reply_worker
        running = asyncio.create_task(old.run())
        await asyncio.wait_for(entered.wait(), timeout=1)
        self.app.action_cancel_reply()
        self.app.submit_prompt('second')
        new = self.app._reply_worker
        release.set()  # Model an already-running adapter which ignores cancellation.
        await asyncio.wait_for(running, timeout=1)
        self.event(old, WorkerState.SUCCESS)
        self.assertIs(self.app._reply_worker, new)
        self.assertTrue(self.app.busy)
        self.assertEqual(self.app.message_count, 3)
        await new.run()
        self.event(new, WorkerState.SUCCESS)
        self.assertEqual(self.app.nodes['#history'].children[-1].message_text, 'Reply second')
    async def test_unmount_suppresses_late_ui_updates(self):
        async def reply(prompt): return 'late'
        self.app.build_reply = reply
        self.app.submit_prompt('first')
        worker = self.app._reply_worker
        self.app.on_unmount()
        await worker.run()
        self.event(worker, WorkerState.SUCCESS)
        self.assertEqual(self.app.message_count, 2)
        self.assertFalse(self.app.submit_prompt('after unmount'))
    async def test_no_forced_follow_when_user_is_reading_history(self):
        self.app.after.clear()
        self.app.nodes['#history'].is_vertical_scroll_end = False
        self.app.add_message('new', 'assistant')
        self.assertEqual(self.app.after, [])
    async def test_follow_callback_rechecks_user_position(self):
        self.app.after.clear()
        history = self.app.nodes['#history']
        self.app.add_message('new', 'assistant')
        fn, args = self.app.after.pop()
        history.scroll_y -= 1
        fn(*args)
        self.assertEqual(history.scrolls, [])
        history.scroll_y = args[1]
        fn(*args)
        self.assertEqual(len(history.scrolls), 1)
        self.assertFalse(history.scrolls[0]['animate'])
    async def test_running_state_does_not_release_current_request(self):
        self.app.submit_prompt('first')
        self.event(self.app._reply_worker, WorkerState.RUNNING)
        self.assertTrue(self.app.busy)
    async def test_invalid_reply_is_a_failure_not_string_coercion(self):
        async def invalid(prompt): return {'unexpected': 'object'}
        self.app.build_reply = invalid
        self.app.submit_prompt('first')
        with self.assertRaises(TypeError): await self.app._reply_worker.run()
        self.assertEqual(self.app.message_count, 2)
    async def test_blank_prompt_is_not_submitted(self):
        self.assertFalse(self.app.submit_prompt(' \n '))
        self.assertEqual(self.app.message_count, 1)
        self.assertIsNone(self.app._reply_worker)


if __name__ == '__main__':
    unittest.main()
