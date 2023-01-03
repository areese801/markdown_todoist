#!/bin/bash

###
### Wrapper script around find_tasks.py.  Useful for automation
### Here, we're relying on pyenv (and thus .python-version) to point to the right python with installed requrements
### If it's not working reliably, try running make_pyenv_venv.sh to re-create the virtual environment
###

## Define the docmd function
        docmd () {
            echo "Running command: [${1}]"
            echo
            eval "${1}"
	    }

thisDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd -P )"

## Resolve Python and Pip Executables
	whichPython=$(which python)
	whichPython3=$(which python3)
	whichPip=$(which pip)
	whichPip3=$(which pip3)
	
	echo "whichPython = ${whichPython}"
	echo "whichPython3 = ${whichPython3}"
	echo "whichPip = ${whichPip}"
	echo "whichPip3 = ${whichPip3}"

	# Found Python?
	if [[ -z "${whichPython}" ]] && [[ -z "${whichPython3}" ]]
	then
		echo "Can't tell which Python to use.  Please install the latest version of Python3"
		exit 1
	else
		# Prefer 'python3' binary over 'python'
		if [[ ! -z "${whichPython3}" ]]
			then
				pythonToUse=${whichPython3}
			else
				pythonToUse=${whichPython}  # We'll assume that it's Python3
		fi

	fi

	echo "pythonToUse = ${pythonToUse}"

	# Found Pip?
		if [[ -z "${whichPip}" ]] && [[ -z "${whichPip3}" ]]
	then
		echo "Can't tell which Pip to use.  Please install the latest version of Pip"
		exit 1
	else
		# Prefer 'pip3' binary over 'ppip'
		if [[ ! -z "${whichPip3}" ]]
			then
				pipToUse=${whichPip3}
			else
				pipToUse=${whichPip}  # We'll assume that it's Python3
		fi
	fi

	echo "pipToUse = ${pipToUse}"

## Best effor to ensure that the right packages are installed
	${pipToUse} install -U -r ${thisDir}/requirements.txt > /dev/null 2>&1 


## Call the Find Tasks script.
	program="${thisDir}/find_tasks.py"

	${pythonToUse} ${program}

