from setuptools import setup, find_packages

setup(
    name='bds_api',
    version='0.0.0',
    description='Brain Data Standards Ontology restful API that wraps data search and query endpoints.',
    url='https://github.com/obophenotype/brain_data_standards_queries',
    author='Huseyin Kir',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Brain Data Standards Ontology',
        'License :: Apache License Version 2.0',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='rest flask swagger flask-restplus bds bdso',

    packages=find_packages(),

    install_requires=['Flask==1.1.1', 'flask-restplus==0.13', 'Werkzeug==0.16.0'],
)
