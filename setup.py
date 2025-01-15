from setuptools import setup, find_packages

import importlib.util
import importlib.machinery

def load_source(modname, filename):
    loader = importlib.machinery.SourceFileLoader(modname, filename)
    spec = importlib.util.spec_from_file_location(modname, filename, loader=loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

version = load_source('jams.version', 'jams/version.py')

# requirements
with open('requirements.txt', 'r') as fh:
    requirements = fh.read().splitlines()

setup(
    name='jams',
    version=version.version,
    description='A JSON Annotated Music Specification for Reproducible MIR Research',
    author='JAMS development crew',
    url='http://github.com/marl/jams',
    download_url='http://github.com/marl/jams/releases',
    packages=find_packages(),
    package_data={'': ['schemata/*.json',
                       'schemata/namespaces/*.json',
                       'schemata/namespaces/*/*.json']},
    long_description='A JSON Annotated Music Specification for Reproducible MIR Research',
    python_requires='>=3.9',
    classifiers=[
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.9",
    keywords='audio music json',
    license='ISC',
    install_requires=[
        'pandas',
        'sortedcontainers>=2.0.0',
        'jsonschema>=3.0.0',
        'numpy>=1.8.0',
        'six',
        'decorator',
        'mir_eval>0.7',
    ],
    extras_require={
        'display': ['matplotlib>=1.5.0'],
        'tests': ['pytest ~= 8.0', 'hypothesis', 'pytest-cov', 'matplotlib>=3'],
    },
    scripts=['scripts/jams_to_lab.py']
)
