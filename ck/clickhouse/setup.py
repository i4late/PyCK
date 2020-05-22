import ast
import os
import pathlib
import typing
import xml.etree.ElementTree


def create_config(
        tcp_port: int,
        http_port: int,
        user: str,
        password: str,
        data_dir: str,
        # notice: recursive type
        config: typing.Dict[str, typing.Any]
) -> None:
    path = pathlib.Path(data_dir)

    tmp_path = path.joinpath('tmp')
    format_schema_path = path.joinpath('format_schema')
    user_files_path = path.joinpath('user_files')
    log_path = path.joinpath('stdout.log')
    errorlog_path = path.joinpath('stderr.log')
    config_path = path.joinpath('config.xml')

    memory_size = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    memory_bound_1 = int(0.6 * memory_size)
    memory_bound_2 = int(0.5 * memory_size)
    memory_bound_3 = int(0.1 * memory_size)

    data = config.copy()

    # add server settings

    data['tcp_port'] = str(tcp_port)
    data['http_port'] = str(http_port)

    if 'listen_host' not in data:
        data['listen_host'] = '0.0.0.0'

    if 'path' not in data:
        data['path'] = str(path)

    if 'tmp_path' not in data:
        data['tmp_path'] = str(tmp_path)

    if 'format_schema_path' not in data:
        data['format_schema_path'] = str(format_schema_path)

    if 'user_files_path' not in data:
        data['user_files_path'] = str(user_files_path)

    if 'mark_cache_size' not in data:
        data['mark_cache_size'] = '5368709120'

    if 'logger' not in data:
        data['logger'] = {
            'log': str(log_path),
            'errorlog': str(errorlog_path),
        }

    if 'query_log' not in data:
        data['query_log'] = {
            'database': 'system',
            'table': 'query_log',
        }

    # add default profile

    def setup_profile(
            data: typing.Dict[str, typing.Any]
    ) -> None:
        if 'max_memory_usage_for_all_queries' not in data:
            data['max_memory_usage_for_all_queries'] = str(memory_bound_1)

        if 'max_memory_usage' not in data:
            data['max_memory_usage'] = str(memory_bound_1)

        if 'max_bytes_before_external_group_by' not in data:
            data['max_bytes_before_external_group_by'] = str(memory_bound_2)

        if 'max_bytes_before_external_sort' not in data:
            data['max_bytes_before_external_sort'] = str(memory_bound_2)

        if 'max_bytes_in_distinct' not in data:
            data['max_bytes_in_distinct'] = str(memory_bound_2)

        if 'max_bytes_before_remerge_sort' not in data:
            data['max_bytes_before_remerge_sort'] = str(memory_bound_3)

        if 'max_bytes_in_set' not in data:
            data['max_bytes_in_set'] = str(memory_bound_3)

        if 'max_bytes_in_join' not in data:
            data['max_bytes_in_join'] = str(memory_bound_3)

        if 'log_queries' not in data:
            data['log_queries'] = '1'

        if 'join_use_nulls' not in data:
            data['join_use_nulls'] = '1'

        if 'join_algorithm' not in data:
            data['join_algorithm'] = 'auto'

        if 'input_format_allow_errors_num' not in data:
            data['input_format_allow_errors_num'] = '100'

        if 'input_format_allow_errors_ratio' not in data:
            data['input_format_allow_errors_ratio'] = '0.01'

        if 'date_time_input_format' not in data:
            data['date_time_input_format'] = 'best_effort'

    if 'profiles' in data:
        assert isinstance(data['profiles'], dict)
    else:
        data['profiles'] = {}

    if user in data['profiles']:
        assert isinstance(data['profiles'][user], dict)
    else:
        data['profiles'][user] = {}

    setup_profile(data['profiles'][user])

    # add default user

    def setup_user(
            data: typing.Dict[str, typing.Any]
    ) -> None:
        if 'profile' not in data:
            data['profile'] = user

        if 'quota' not in data:
            data['quota'] = user

        if 'password' not in data:
            data['password'] = password

        if 'networks' not in data:
            data['networks'] = {
                'ip': '::/0',
            }

    if 'users' in data:
        assert isinstance(data['users'], dict)
    else:
        data['users'] = {}

    if user in data['users']:
        assert isinstance(data['users'][user], dict)
    else:
        data['users'][user] = {}

    setup_user(data['users'][user])

    # add default quota

    if 'quotas' in data:
        assert isinstance(data['quotas'], dict)
    else:
        data['quotas'] = {}

    if user in data['quotas']:
        assert isinstance(data['quotas'][user], dict)
    else:
        data['quotas'][user] = {}

    # generate xml

    def build_xml(
            # notice: recursive type
            data: typing.Any,
            node: xml.etree.ElementTree.Element
    ) -> None:
        if isinstance(data, dict):
            for key, value in data.items():
                assert isinstance(key, str)

                subnode = xml.etree.ElementTree.SubElement(node, key)
                build_xml(value, subnode)
        else:
            assert isinstance(data, str)

            node.text = data

    root = xml.etree.ElementTree.Element('yandex')

    for key, value in data.items():
        subnode = xml.etree.ElementTree.SubElement(root, key)
        build_xml(value, subnode)

    # write xml

    config_path.open('wb').write(xml.etree.ElementTree.tostring(root))


if __name__ == '__main__':
    create_config(**ast.literal_eval(input()))
