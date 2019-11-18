import pathlib
import sys
import types

from ck.connection import http
from ck.connection import process
from ck.connection import ssh


dir_path = pathlib.Path(__file__).parent
ck_path = dir_path.joinpath('clickhouse')


class CKError(RuntimeError):
    pass


class PassiveSession(object):
    def __init__(
        self,
        host='localhost',
        tcp_port=9000,
        http_port=8123,
        ssh_port=22,
        ssh_username=None,
        ssh_password=None,
        ssh_public_key=None,
        ssh_command_prefix=''
    ):
        assert type(host) is str
        assert type(tcp_port) is int
        assert type(http_port) is int
        assert ssh_username is None or type(ssh_username) is str
        assert ssh_password is None or type(ssh_password) is str
        assert ssh_public_key is None or type(ssh_public_key) is str
        assert type(ssh_command_prefix) is str

        self._host = host
        self._tcp_port = tcp_port
        self._http_port = http_port
        self._ssh_client = ssh.connect(
            host,
            ssh_port,
            ssh_username,
            ssh_password,
            ssh_public_key
        )
        self._ssh_command_prefix = ssh_command_prefix

    def _connect(
        self,
        gen_stdin,
        gen_stdout,
        gen_stderr,
        method='http'
    ):
        assert type(gen_stdin) is types.GeneratorType
        assert type(gen_stdout) is types.GeneratorType
        assert type(gen_stderr) is types.GeneratorType
        assert method in {'tcp', 'http', 'ssh'}

        if method == 'tcp':
            join_raw = process.run(
                [
                    str(ck_path),
                    'client',
                    '--host',
                    self._host,
                    '--port',
                    str(self._tcp_port),
                ],
                gen_stdin,
                gen_stdout,
                gen_stderr
            )
            ok = 0
        elif method == 'http':
            join_raw = http.run(
                self._host,
                self._http_port,
                '/',
                gen_stdin,
                gen_stdout,
                gen_stderr
            )
            ok = 200
        elif method == 'ssh':
            join_raw = ssh.run(
                self._ssh_client,
                [
                    *(
                        []
                        if self._ssh_command_prefix is None
                        else [self._ssh_command_prefix]
                    ),
                    str(ck_path),
                    'client',
                    '--port',
                    str(self._tcp_port),
                ],
                gen_stdin,
                gen_stdout,
                gen_stderr
            )
            ok = 0

        def join():
            return join_raw() == ok

        return join

    def query_async(
        self,
        query_text,
        gen_in=None,
        gen_out=None,
        method='http'
    ):
        assert type(query_text) is str
        assert gen_in is None or type(gen_in) is types.GeneratorType
        assert gen_out is None or type(gen_out) is types.GeneratorType
        assert method in {'tcp', 'http', 'ssh'}

        def make_stdin():
            yield f'{query_text}\n'.encode()

            if gen_in is not None:
                yield from gen_in

        def make_stdout():
            if gen_out is not None:
                yield from gen_out

        error_text_list = []

        def make_stderr():
            while True:
                error_text_list.append((yield).decode())

        join_raw = self._connect(
            make_stdin(),
            make_stdout(),
            make_stderr(),
            method
        )

        def join():
            if not join_raw():
                raise CKError(
                    self._host,
                    self._tcp_port,
                    self._http_port,
                    query_text,
                    ''.join(error_text_list)
                )

        return join

    def query_sync(
        self,
        query_text,
        gen_in=None,
        gen_out=None,
        method='http'
    ):
        assert type(query_text) is str
        assert gen_in is None or type(gen_in) is types.GeneratorType
        assert gen_out is None or type(gen_out) is types.GeneratorType
        assert method in {'tcp', 'http', 'ssh'}

        return self.query_async(query_text, gen_in, gen_out, method)()
