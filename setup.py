from distutils.core import setup

from setuptools import find_packages

setup(
    name='espresso',
    version='1.2.0',
    packages=find_packages(),
    url='https://github.com/labbcb/espresso-caller',
    license='',
    author='Welliton de Souza, Benilton Carvalho',
    author_email='well309@gmail.com, benilton@unicamp.br',
    description='Automates WGS/WES genomic variant calling',
    requires=['click', 'requests'],
    include_package_data=True,
    entry_points='''
        [console_scripts]
        espresso=espresso.scripts.espresso:cli
    ''',
)
