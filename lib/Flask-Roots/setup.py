from distutils.core import setup

setup(
    name='Flask-Roots',
    version='0.0.1',
    description='Lightweight personal git server.',
    url='http://github.com/mikeboers/Flask-Roots',
    
    packages=['flask_roots'],
    
    author='Mike Boers',
    author_email='flask-roots@mikeboers.com',
    license='BSD-3',
    
    entry_points={
        'console_scripts': [
        ],
    },

    install_requires='''

        Baker
        jsmin
        watchdog

        Flask

        Flask-Mako
        Markdown
        PyHAML

        Flask-SQLAlchemy
        sqlalchemy-migrate

        Flask-Mail
        
        PIL
        Flask-Images

        Flask-Login
        Flask-ACL

        gunicorn
        gevent
    
    ''',

    classifiers=[
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
    ],
    
)
