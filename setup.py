from setuptools import setup, find_packages

import imp

version = imp.load_source('pyjams.version', 'pyjams/version.py')

setup(
    name='pyjams',
    version=version.version,
    description='A JSON Annotated Music Specification for Reproducible MIR Research',
    author='JAMS development crew',
    url='http://github.com/marl/jams',
    download_url='http://github.com/marl/jams/releases',
    packages=find_packages(),
    package_data={'': ['schema/*.json',
                       'schema/namespaces/*.json',
                       'schema/namespaces/*/*.json']},
    include_package_data=True,
    long_description="""A python module for audio and music processing.""",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='audio music json',
    license='BSD',
    install_requires=[
        'json',
        'pandas',
        'jsonschema'
        'numpy >= 1.8.0',
        'six',
        'decorator',
    ],
    extras_require={
        'docs': ['numpydoc']
    }
)
