from setuptools import setup

setup(
    name='SquidsTools',
    include_package_data=True,
    version='0.0.2',
    packages=['SquidsTools'],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        'SquidsTools': ['web/*.html', 'web/css/*.css',
                        'web/js/*.js', 'data/*.csv'],
    },
    url='https://github.com/AndruQuiroga/Squid-s-Tools',
    entry_points={
        'console_scripts': [
            'SquidsTools=SquidsTools.run:main'
        ]
    },
    license='',
    author='Dreski',
    author_email='',
    description='',
    install_requires=['numpy', 'pandas', 'eel'],
)
