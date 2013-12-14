from setuptools import setup, find_packages

setup(
    name='uwiki',
    version='0.0.1',
    description='A micro wiki.',
    url='http://github.com/mikeboers/uWiki',
    
    packages=find_packages(),
    
    author='Mike Boers',
    author_email='uwiki@mikeboers.com',
    license='BSD-3',
    
    entry_points={
        'console_scripts': [
            'uwiki-account = uwiki.commands.account:main',
        ],
    },
    
)
