#!/bin/bash

## This program sets up a python virtual environment at a given path.  It accepts and requires just a single parameter which is a fully 
## qualified path to the parent folder in which the virtual environment should be created.  Additionally, a requirements.txt file should
## exist in that path ahead of time.  The virtual environment folder will be a 'peer' of requirements.txt 


## Define the showHelp() function
	showHelp(){
		echo
		echo "You called the program with the help parameter. Or you called it incorrectly.  Help is below."
		echo "This script accepts a single parameter:  A path to an (existing) directory in which a python virtual env"
		echo "should be created.  Additionally, a requirements.txt file should exist in that directory ahead of time.  If a virtual environment"
		echo "already exists, the program will take no action.  If you wish to re-create a virtual environment, invoke this program with the -f flag"
		echo
		echo "Positional args are as follows:"
		echo "\t (Required) Fully Qualified Path to target parent dir of the virtual environment (do not include virtualenv subfolder)" 
		echo "\t (Optional) [-f]. If the -'f' flag is passed to the program a new virtual environment will be created even if one already exists" 
		echo 
		echo "Example usage:"
		echo "\t. make_env.sh /path/to/somewhere/  <-- If not present at invocation, results in a virtual environment at '/path/to/somewhere/venv'"
		echo "\t. make_env.sh /path/to/somewhere/ -f  <-- Results in a virtual environment at '/path/to/somewhere/venv' even if one existed there previously"
	}

## Define the docmd function
	docmd () {
		echo "Running command: [${1}]" 
		eval "${1}"
	}

## Define the echocmd function.  Good for debugging
	echocmd () {
		echo "The command is: ${1}" 
		echo
	}

## Define the refreshFromRequirements function
	refreshFromRequirements() {
		echo "Refreshing from requirements.txt"

		echo "This program assumes you've got pip3 installed.  If that's not the case, please install it and call this program again."
		docmd "pip3 install virtualenv"  # See:  http://www.pythonforbeginners.com/basics/how-to-use-python-virtualenv
		docmd "source ${targetDir}/bin/activate" # Important step!
		
		echo "The value of VIRTUAL_ENV variable is [$VIRTUAL_ENV]" # If we see a value here, we're sure that activate worked.
		
		docmd "which python"
		docmd "python --version"
		
		docmd "pip install -U -r ${requirementsFile}"
		docmd "deactivate"
	}

## Show help then exit if the user calls the program like this:  'make_env.sh help' or something equeally obvious
	if [[ "$1" == "help" ]] || [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]
		then
		showHelp && return 1
	fi


# Handle variables
		
	# Handle targetParentDir, which is our anchor for many other vars
	if [[ -z "${1}" ]]
		then
			# Not passed in, default to pwd
			targetParentDir=$(pwd -P)
			echo "No target directory was passed.  Defaulting to pwd: ${targetParentDir} "
		else
			targetParentDir=$1
		fi

	# Handle the rest of the variables
	# targetDir=${targetParentDir}/virtualenv
	targetDir=${targetParentDir}/venv  # Jetbrains fleet automatically detects this name.  See:  https://www.jetbrains.com/help/fleet/getting-started-with-python.html#python-interpreter
	requirementsFile=${targetParentDir}/requirements.txt
	forceRecreate=$2
	echo "targetParentDir = ${targetParentDir}"
	echo "targetDir = ${targetDir}"
	echo "requirementsFile = ${requirementsFile}"
	echo "forceRecreate = ${forceRecreate}"


## Check that the destination directory (parent of virtual env) exists
	if [[ ! -d "${targetParentDir}" ]]
		then
		echo "Error!  The path [${targetParentDir}] does not exists.  Exiting"
		return 1
	fi

## Check that the requirements.txt file exists at the parent dir
	if [[ ! -f "${requirementsFile}" ]]
		then
		echo "Error!  There is no requirements.txt file under [${targetParentDir}].  Exiting"
		return 1	
	fi

## Check if the virtual environment folder already exists
	if [[ "${forceRecreate}" != "-f" ]]
	then
		if [[ -d "${targetDir}" ]]
			then
				echo "There is already a virtual environment folder at [${targetDir}].  The program will refresh from requirements.txt then exit."
				
				refreshFromRequirements
				
				return 1
		fi
	fi

###
### NOTE:  If we didn't exit in the block above, then forceRecreate was -f, thus, we'll nuke the target path and re-create it
###

## If we get here, we've passed ll preliminary checks
	echo "All preliminary checks passed!"

## Make target path
	docmd "rm -rf ${targetDir}" # Here, we're either forcing a rebuild or we'd have exited by now
	docmd "mkdir -p ${targetDir}"

## Setup the virtual environment	
	docmd "virtualenv --python=python3 ${targetDir}"

## Install all requirements
	refreshFromRequirements