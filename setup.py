from distutils.core import setup

from setuptools import find_packages

setup(
    name='wfauto',
    version='1.0.0',
    packages=find_packages(),
    url='https://github.com/labbcb/workflow-wfauto',
    license='',
    author='Welliton Souza',
    author_email='well309@gmail.com',
    description='Automates genomic data processing',
    requires=['click'],
    include_package_data=True,
    entry_points='''
        [console_scripts]
        wfauto=wfauto.scripts.wfauto:cli
    ''',
)
