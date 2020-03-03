from setuptools import setup



setup(
    name = 'acwingcli',
    version = '0.2.0',
    packages = ['acwingcli'],
    entry_points = { 'console_scripts': ['acwingcli = acwingcli.__main__:main'] },
    package_data = {  # Optional
        'acwingcli' : ['assets/data.json']
    })
