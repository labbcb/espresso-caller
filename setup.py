from distutils.core import setup

from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='espresso-caller',
    version='1.2.3',
    packages=find_packages(),
    url='https://github.com/labbcb/espresso-caller',
    license='MIT',
    author='Welliton de Souza, Benilton Carvalho',
    author_email='well309@gmail.com, benilton@unicamp.br',
    description='Automated and reproducible tool for identifying genomic variations at scale',
    long_description=long_description,
    long_description_content_type="text/markdown",
    requires=['click', 'requests'],
    include_package_data=True,
    entry_points='''
        [console_scripts]
        espresso=espresso.espresso:cli
    ''',
)
