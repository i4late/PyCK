from ck import query


def test_query_escape_text() -> None:
    assert query.ast.escape_text('\x00\\\n', '\'') == '\'\\0\\\\\\n\''
    assert query.ast.escape_text('test!', '!') == '!test\\!!'


def test_query_escape_buffer() -> None:
    assert query.ast.escape_buffer(b'\x00\\\xff', '\'') == '\'\\0\\\\\\xff\''
    assert query.ast.escape_buffer(b'test!', '!') == '!test\\!!'


def test_query_escape_value() -> None:
    assert query.ast.escape_value(None) == 'null'
    assert query.ast.escape_value(Ellipsis) == '*'
    assert query.ast.escape_value(False) == 'false'
    assert query.ast.escape_value(True) == 'true'
    assert query.ast.escape_value(123) == '123'
    assert query.ast.escape_value(123.) == '123.0'
    assert query.ast.escape_value(123e456) == 'inf'
    assert query.ast.escape_value(1 + 2j) == 'tuple(1.0, 2.0)'
    assert query.ast.escape_value([]) == 'array()'
    assert query.ast.escape_value([1, 2, 3]) == 'array(1, 2, 3)'
    assert query.ast.escape_value(tuple()) == 'tuple()'
    assert query.ast.escape_value((1, 2, 3)) == 'tuple(1, 2, 3)'
    assert query.ast.escape_value(range(123)) == 'range(0, 123, 1)'
    assert query.ast.escape_value(range(1, 2, 3)) == 'range(1, 2, 3)'
    assert query.ast.escape_value('test\n') == '\'test\\n\''
    assert query.ast.escape_value(b'test\xff') == '\'test\\xff\''
    assert query.ast.escape_value(bytearray(b'test\xff')) == '\'test\\xff\''
    assert query.ast.escape_value(memoryview(b'test\xff')) == '\'test\\xff\''
    assert query.ast.escape_value(set()) == 'array()'
    assert query.ast.escape_value({1, 2, 3}) == 'array(1, 2, 3)'
    assert query.ast.escape_value(frozenset()) == 'array()'
    assert query.ast.escape_value(frozenset({1, 2, 3})) == 'array(1, 2, 3)'
    assert query.ast.escape_value({}) == 'array()'
    assert query.ast.escape_value({1: 2}) == 'array(tuple(1, 2))'


def test_query_box() -> None:
    value = query.ast.Value(1)
    identifier = query.ast.Identifier('1')

    assert query.ast.box(1).render_expression() == value.render_expression()
    assert query.ast.box(identifier) is identifier


def test_query_unbox() -> None:
    value = query.ast.Value(1)
    identifier = query.ast.Identifier('1')

    assert query.ast.unbox(value) == 1
    assert query.ast.unbox(identifier) is identifier


def test_query_value() -> None:
    value_1 = query.ast.Value(1)
    value_2 = query.ast.Value(['1', 2, 3])

    assert value_1.render_expression() == '1'
    assert value_1.render_statement() == 'select 1'
    assert value_2.render_expression() == 'array(\'1\', 2, 3)'
    assert value_2.render_statement() == 'select array(\'1\', 2, 3)'


def test_query_identifier() -> None:
    identifier_1 = query.ast.Identifier('test')
    identifier_2 = query.ast.Identifier('test`')

    assert identifier_1.render_expression() == '`test`'
    assert identifier_1.render_statement() == 'select `test`'
    assert identifier_2.render_expression() == '`test\\``'
    assert identifier_2.render_statement() == 'select `test\\``'


def test_query_call() -> None:
    identifier = query.ast.Identifier('test')
    value = query.ast.Value(1)
    call_1 = query.ast.Call('test', [])
    call_2 = query.ast.Call(identifier, [value, call_1])

    assert call_1.render_expression() == 'test()'
    assert call_1.render_statement() == 'select test()'
    assert call_2.render_expression() == '`test`(1, test())'
    assert call_2.render_statement() == 'select `test`(1, test())'


def test_query_initial() -> None:
    initial_1 = query.ast.Initial('test')
    initial_2 = query.ast.Initial('__test__test__')

    assert initial_1.render_expression() == '(test)'
    assert initial_1.render_statement() == 'test'
    assert initial_2.render_expression() == '(test test)'
    assert initial_2.render_statement() == 'test test'


def test_query_simple_clause() -> None:
    initial = query.ast.Initial('select')
    simple_clause_1 = query.ast.SimpleClause(initial, 'test')
    simple_clause_2 = query.ast.SimpleClause(initial, '__test__test__')

    assert simple_clause_1.render_expression() == '(select test)'
    assert simple_clause_1.render_statement() == 'select test'
    assert simple_clause_2.render_expression() == '(select test test)'
    assert simple_clause_2.render_statement() == 'select test test'


def test_query_list_clause() -> None:
    initial = query.ast.Initial('select')
    value = query.ast.Value(1)
    list_clause_1 = query.ast.ListClause(initial, [])
    list_clause_2 = query.ast.ListClause(initial, [value, list_clause_1])

    assert list_clause_1.render_expression() == '(select)'
    assert list_clause_1.render_statement() == 'select'
    assert list_clause_2.render_expression() == '(select 1, (select))'
    assert list_clause_2.render_statement() == 'select 1, (select)'
