#!/bin/bash

###
### Wrapper script around migrate_tasks.py.  Useful for automation
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
thisProgramNoExtension=${0%.*}

## Do a check on the pid from the last time this program was run, to make sure we don't step on our own toes
	pidFileNameShort=${thisProgramNoExtension}.pid
	pidFileName="${thisDir}/${pidFileNameShort}"
	touch ${pidFileName}
	lastPID=$(< ${pidFileName})
	thisPID=$$

	## Bail out if lastPID is still running 
	if [[ ! -z "${lastPID}" ]] && [[ $(ps ${lastPID} | wc -l) -ne 1 ]]  # wc still returns 1 line if the process doesn't exist (headers)
	then
		echo "The previous pid [${lastPID}] is still running.  The program will exit."
		exit
	else
		echo "${thisPID}" > ${pidFileName}
	fi

echo "thisProgramNoExtension = ${thisProgramNoExtension}"
echo "pidFileNameShort = ${pidFileNameShort}"
echo "pidFileName = ${pidFileName}"

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
		# Prefer 'pip3' binary over 'pip'
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
	program="${thisDir}/migrate_tasks.py"

	${pythonToUse} ${program}
