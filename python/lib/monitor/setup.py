from setuptools import setup, find_namespace_packages

try:
    with open('README.md', 'r') as readme:
        long_description = readme.read()
except:
    long_description = ''

exec(open('dmod/monitor/_version.py').read())

setup(
    name='dmod-monitor',
    version=__version__,
    description='',
    long_description=long_description,
    author='',
    author_email='',
    url='',
    license='',
    install_requires=['docker', 'Faker', 'dmod-core>=0.1.0', 'dmod-communication>=0.4.2', 'dmod-redis>=0.1.0',
                      'dmod-scheduler>=0.5.0'],
    packages=find_namespace_packages(exclude=('test', 'src'))
)
