from setuptools import setup



setup(
    name = 'acwingcli',
    version = '0.2.0',
    packages = ['acwingcli'],
    include_package_data = True,
    entry_points = { 'console_scripts': ['acwingcli = acwingcli.__main__:main'] },
    )
