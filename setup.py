from setuptools import setup, find_packages

setup(
    name='syntaxerrors',
    version='0.0.1',
    description='Report better SyntaxErrors',
    author='Carl Friedrich Bolz-Tereick',
    author_email='cfbolz@gmx.de',
    packages=['syntaxerrors'],
    package_dir={'': 'src'},
    include_package_data=True,
)
