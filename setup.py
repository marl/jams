from setuptools import setup, find_packages

from importlib.util import spec_from_file_location, module_from_spec

def load_source(module, file_path):
    """ From https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly """
    spec = spec_from_file_location('jams.version', 'jams/version.py')
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

version = load_source('jams.version', 'jams/version.py')

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
    classifiers=[
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8"
    ],
    keywords='audio music json',
    license='ISC',
    install_requires=[
        'pandas',
        'sortedcontainers>=2.0.0',
        'pyrsistent<0.15; python_version=="3.4"',
        'jsonschema>=3.0.0',
        'numpy>=1.8.0',
        'six',
        'decorator',
        'mir_eval>=0.5',
    ],
    extras_require={
        'display': ['matplotlib>=1.5.0'],
        'tests': ['pytest ~= 8.0', 'pytest-cov', 'matplotlib>=3'],
    },
    scripts=['scripts/jams_to_lab.py']
)
