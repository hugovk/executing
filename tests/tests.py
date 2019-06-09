# -*- coding: utf-8 -*-
from __future__ import print_function, division

import ast
import inspect
import linecache
import os
import time
import unittest

from executing_node import Source, only, NotOneValueFound, PY3, SourceFinder


class TestStuff(unittest.TestCase):

    # noinspection PyTrailingSemicolon
    def test_semicolons(self):
        # @formatter:off
        tester(1); tester(2); tester(3)
        tester(9
               ); tester(
            8); tester(
            99
        ); tester(33); tester([4,
                               5, 6, [
                                7]])
        # @formatter:on

    def test_decorator(self):
        @empty_decorator
        @decorator_with_args(tester('123'), x=int())
        @tester(list(tuple([1, 2])), returns=empty_decorator)
        @tester(
            list(
                tuple(
                    [3, 4])),
            returns=empty_decorator)
        @empty_decorator
        @decorator_with_args(
            str(),
            x=int())
        @tester(list(tuple([5, 6])), returns=empty_decorator)
        @tester(list(tuple([7, 8])), returns=empty_decorator)
        @empty_decorator
        @decorator_with_args(tester('sdf'), x=tester('123234'))
        def foo():
            pass

    def test_comprehensions(self):
        # Comprehensions can be separated if they contain different names
        str([{tester(x) for x in [1]}, {tester(y) for y in [1]}])
        # or are on different lines
        str([{tester(x) for x in [1]},
             {tester(x) for x in [1]}])
        # or are of different types
        str([{tester(x) for x in [1]}, list(tester(x) for x in [1])])
        # but not if everything is the same
        with self.assertRaises(NotOneValueFound):
            str([{tester(x) for x in [1]}, {tester(x) for x in [2]}])

    def test_lambda(self):
        self.assertEqual(
            (lambda x: (tester(x), tester(x)))(tester(3)),
            (3, 3),
        )
        (lambda: (lambda: tester(1))())()
        self.assertEqual(
            (lambda: [tester(x) for x in tester([1, 2])])(),
            [1, 2],
        )

    def test_closures_and_nested_comprehensions(self):
        x = 1
        # @formatter:off
        str({tester(a+x): {tester(b+x): {tester(c+x) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})

        def foo():
            y = 2
            str({tester(a+x): {tester(b+x): {tester(c+x) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})
            str({tester(a+y): {tester(b+y): {tester(c+y) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})
            str({tester(a+x+y): {tester(b+x+y): {tester(c+x+y) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})

            def bar():
                z = 3
                str({tester(a+x): {tester(b+x): {tester(c+x) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})
                str({tester(a+y): {tester(b+y): {tester(c+y) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})
                str({tester(a+x+y): {tester(b+x+y): {tester(c+x+y) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})
                str({tester(a+x+y+z): {tester(b+x+y+z): {tester(c+x+y+z) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})

            bar()

        foo()
        # @formatter:on

    def test_indirect_call(self):
        dict(x=tester)['x'](tester)(3)

    def test_compound_statements(self):
        with self.assertRaises(TypeError):
            try:
                for _ in tester([1, 2, 3]):
                    while tester(0):
                        pass
                    else:
                        tester(4)
                else:
                    tester(5)
                    raise ValueError
            except tester(ValueError):
                tester(9)
                raise TypeError
            finally:
                tester(10)

        # PyCharm getting confused somehow?
        # noinspection PyUnreachableCode
        str()

        with self.assertRaises(tester(Exception)):
            if tester(0):
                pass
            elif tester(0):
                pass
            elif tester(1 / 0):
                pass

    def test_generator(self):
        def gen():
            for x in [1, 2]:
                yield tester(x)

        gen2 = (tester(x) for x in tester([1, 2]))

        assert list(gen()) == list(gen2) == [1, 2]

    def test_future_import(self):
        print(1 / 2)
        tester(4)

    def test_many_calls(self):
        node = None
        start = time.time()
        for i in range(100000):
            new_node = Source.executing_node(inspect.currentframe())
            if node is None:
                node = new_node
            else:
                self.assertIs(node, new_node)
        self.assertLess(time.time() - start, 1)

    def test_source_finder(self):
        code_filename = '<code filename>'
        dir_name = os.path.abspath(
            os.path.dirname(__file__),
        )
        test_file_filename = os.path.join(
            dir_name,
            'source_test_file.py',
        )
        not_code_filename = os.path.join(
            dir_name,
            'not_code.txt',
        )

        with open(test_file_filename) as f:
            test_file_text = f.read()

        def check(exception, filename=code_filename, **globs):
            code = compile(test_file_text, code_filename, 'exec')
            exec(code, globs)
            frame = globs['frame']
            setattr(Source, '__source_cache', {})
            if exception:
                with self.assertRaises(Exception):
                    Source.for_frame(frame)
            else:
                source = Source.for_frame(frame)
                self.assertEqual(source.text, test_file_text)
                self.assertEqual(filename, source.filename)

        check(True)

        linecache.cache[code_filename] = (
            len(test_file_text),
            None,
            [line + '\n' for line in test_file_text.splitlines()],
            code_filename
        )
        check(False)

        check(False, __file__=not_code_filename)
        check(False, __file__=test_file_filename, filename=test_file_filename)
        del linecache.cache[code_filename]
        check(False, __file__=test_file_filename, filename=test_file_filename)
        check(True, __file__=__file__)

        check(True, __loader__=TestSourceLoader('x = 1'))
        check(False, __loader__=TestSourceLoader(test_file_text))

    def test_decode_source(self):
        def check(source, encoding, exception=None, matches=True):
            encoded = source.encode(encoding)
            if exception:
                with self.assertRaises(exception):
                    SourceFinder.decode_source(encoded)
            else:
                decoded = SourceFinder.decode_source(encoded)
                if matches:
                    self.assertEqual(decoded, source)
                else:
                    self.assertNotEqual(decoded, source)

        check(u'# coding=utf8\né', 'utf8')
        check(u'# coding=gbk\né', 'gbk')

        check(u'# coding=utf8\né', 'gbk', exception=UnicodeDecodeError)
        check(u'# coding=gbk\né', 'utf8', matches=False)

        # In Python 3 the default encoding is assumed to be UTF8
        if PY3:
            check(u'é', 'utf8')
            check(u'é', 'gbk', exception=SyntaxError)

    def test_multiline_strings(self):
        tester('a')
        tester('''
            ab''')
        tester('''
                    abc
                    def
                    '''
               )
        str([
            tester(
                '''
                123
                456
                '''
            ),
            tester(
                '''
                345
                456786
                '''
            ),
        ])
        tester(
            [
                '''
                123
                456
                '''
                '''
                345
                456786
                '''
                ,
                '''
                123
                456
                ''',
                '''
                345
                456786
                '''
            ]
        )


class TestSourceLoader(object):
    def __init__(self, text):
        self.text = text

    def get_source(self, *_args, **_kwargs):
        return self.text


def tester(arg, returns=None):
    frame = inspect.currentframe().f_back
    call = Source.executing_node(frame)
    result = eval(
        compile(ast.Expression(only(call.args)), '<>', 'eval'),
        frame.f_globals,
        frame.f_locals,
    )
    assert result == result, (result, arg)
    if returns is None:
        return arg
    return returns


assert tester([1, 2, 3]) == [1, 2, 3]


def empty_decorator(f):
    return f


def decorator_with_args(*_, **__):
    return empty_decorator


if __name__ == '__main__':
    unittest.main()
