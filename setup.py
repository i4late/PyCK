import setuptools


if __name__ == '__main__':
    setuptools.setup(
        install_requires=['paramiko'],
        name='ck',
        package_data={'ck': ['clickhouse']},
        packages=['ck'],
        zip_safe=False
    )