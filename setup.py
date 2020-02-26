from setuptools import setup


setup(
    name = 'acwingcli',
    version = '0.1.0',
    packages = ['acwingcli'],
    entry_points = { 'console_scripts': ['acwingcli = acwingcli.__main__:main'] }
    )
