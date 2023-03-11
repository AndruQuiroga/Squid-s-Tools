from setuptools import setup

setup(
    name='SquidsTools',
    include_package_data=True,
    version='0.0.1',
    packages=['SquidsTools'],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.html', '*.css', '*.js', '*.csv'],
    },
    url='https://github.com/AndruQuiroga/Squid-s-Tools',
    license='',
    author='Dreski',
    author_email='',
    description='',
    install_requires=['setuptools-git', 'numpy', 'pandas', 'eel'],
)
