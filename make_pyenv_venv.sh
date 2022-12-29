#!/bin/bash

###
### Makes a python virtual environment.  
### All of the steps wrapped by install_latest_pyenv_python.sh and the rest of the turtles all the way down should have been completed by the time this script is run.
###

# Exit when any command fails.  Un-comment line below to assist with troubleshooting
# set -e

## Define the docmd function
        docmd () {
            echo "Running command: [${1}]"
            echo
            eval "${1}"
	    }

thisDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd -P )"

## Install the latest stable version of python
	docmd "source ${thisDir}/install_latest_pyenv_python.sh"


## Determine the latest INSTALLED stable version of python
## Note that 'pyenv install --list' lists AVAILABLE versions of python, while 'pyenv versions' lists INSTALLED versions of python
	latestStableInstalledPython=$(pyenv versions --bare | grep --color=never -E '^\s*\d' | grep --color=never -v -i -E '[a-z]+' | tail -n 1 | tr -d ' ')
	echo "The latest INSTALLED (not to be confused with AVAILABLE) stable version of python seems to be:  ${latestStableInstalledPython}"

## Create a virtual environment for this project
## See:  https://realpython.com/intro-to-pyenv/#creating-virtual-environments
	environmentName=$(basename "${thisDir}")
	docmd "pyenv virtualenv ${latestStableInstalledPython} ${environmentName}" # Creates ~/.pyenv/versions/markdown_todoist

## Activate the virutal environment
	
	# These Evals help avoid an error like that below.  Ideally, the user will have these in their ~/.bashrc or ~/.zshrc files but we won't count on that
	# See:  https://stackoverflow.com/questions/45577194/failed-to-activate-virtualenv-with-pyenv
		# Failed to activate virtualenv.

		# Perhaps pyenv-virtualenv has not been loaded into your shell properly.
		# Please restart current shell and try again.

		eval "$(pyenv init -)"  
		eval "$(pyenv virtualenv-init -)"

	docmd "pyenv local ${environmentName}"
	docmd "pyenv activate ${environmentName}" # Documentation says:  "If you did not configure eval "$(pyenv virtualenv-init -)" to run in your shell, you can manually activate/deactivate your Python versions with this.  See:  https://realpython.com/intro-to-pyenv/#activating-your-versions
	docmd "pyenv which python" #Proof!
	docmd "pyenv which pip" #Proof!

## Install the required packages
	requirementsFile="${thisDir}/requirements.txt"
	docmd "touch ${requirementsFile}"
	docmd "pip install -U -r ${requirementsFile}"
	docmd "pip freeze | tee ${thisDir}/freeze.txt"

