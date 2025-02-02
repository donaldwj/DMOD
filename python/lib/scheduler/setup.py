from setuptools import setup, find_namespace_packages

try:
    with open('README.md', 'r') as readme:
        long_description = readme.read()
except:
    long_description = ''

exec(open('dmod/scheduler/_version.py').read())

setup(
    name='dmod-scheduler',
    version=__version__,
    description='',
    long_description=long_description,
    author='',
    author_email='',
    url='',
    license='',
    install_requires=['docker', 'Faker', 'dmod-communication>=0.8.0', 'dmod-modeldata>=0.7.1', 'dmod-redis>=0.1.0',
                      'dmod-core>=0.2.0', 'cryptography', 'uri', 'pyyaml'],
    packages=find_namespace_packages(exclude=('test', 'src'))
)

