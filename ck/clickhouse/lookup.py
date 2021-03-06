import pathlib


def default_data_dir() -> str:
    return str(pathlib.Path.home().joinpath('.ck_data'))


def binary_file() -> str:
    path = pathlib.Path(__file__).parent.joinpath('clickhouse')

    if path.exists():
        return str(path)

    return 'clickhouse'


if __name__ == '__main__':
    print(default_data_dir())
    print(binary_file())
