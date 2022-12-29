#!/bin/bash

###
### A best (but likely not perfect) attempt to install the latest python via pyenv
### pyenv should have been installed ahead of time via the install_pyenv.sh script
###

## Define the docmd function
        docmd () {
            echo "Running command: [${1}]"
            echo
            eval "${1}"
	    }

thisDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd -P )"

## Install pyenv
	docmd "source ${thisDir}/install_pyenv.sh"

## Get the latest stable python version number (or probably something close enough)
	## Here, we're using pyenv install --list, which lists all available python versions. There are many. See:  https://realpython.com/intro-to-pyenv/#using-pyenv-to-install-python
	 ## Of these, we filter down just to those that start with a digit (e.g. removing anaconda, miniconda, jupyter, etc..)
	  ## Of these, we filter to those that have no letters in their version number (e.g. removing 'dev', etc)
	   ## Of these, and relying on the fact that 'pyenv install --list' returns results in ascending order (not alphabetically) by version, we take the last and remove leading spaces
		latestStablePython=$(pyenv install --list | grep --color=never -E '^\s*\d' | grep --color=never -v -i -E '[a-z]+' | tail -n 1 | tr -d ' ')
		echo "The latest stable python version seems to be: ${latestStablePython}"

## Having the latest version number from above, install it
## Here, -s skips the install if it already exists.  -v is verbose
	docmd "pyenv install -s -v ${latestStablePython}"


