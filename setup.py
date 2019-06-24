from distutils.core import setup

setup(
    name='automator',
    version='1.0.0',
    packages=[''],
    url='https://github.com/labbcb/workflow-automator',
    license='',
    author='Welliton Souza',
    author_email='well309@gmail.com',
    description='Automates genomic data processing',
    requires=['click'],
    entry_points='''
        [console_scripts]
        automator=automator.scripts.automator:cli
    ''',
)
