#!/bin/sh

ENV_NAME="test-environment"
set -e

conda_create ()
{

    hash -r
    conda config --set always_yes yes --set changeps1 no
    conda update -q conda
    conda config --add channels pypi
    conda info -a
    deps='six coverage numpy scipy pandas decorator sphinx matplotlib'

    conda create -q -n $ENV_NAME "python=$TRAVIS_PYTHON_VERSION" $deps
}

src="$HOME/env/miniconda$TRAVIS_PYTHON_VERSION"
if [ ! -d "$src" ]; then
    mkdir -p $HOME/env
    pushd $HOME/env
    
        # Download miniconda packages
        wget http://repo.continuum.io/miniconda/Miniconda-3.16.0-Linux-x86_64.sh -O miniconda.sh;

        # Install both environments
        bash miniconda.sh -b -p $src

        export PATH="$src/bin:$PATH"
        conda_create 
        source activate $ENV_NAME
        # later versions than 5.2 do not support python 3.4 anymore
        pip install PyYAML==5.2; python_version==3.4
        pip install python-coveralls
        source deactivate
    popd
else
    echo "Using cached dependencies"
fi
