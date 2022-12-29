#!/bin/bash

###
### Wrapper script around find_tasks.py.  Useful for automation
### Here, we're relying on pyenv (and thus .python-version) to point to the right python with installed requrements
### If it's not working reliably, try running make_pyenv_venv.sh to re-create the virtual environment
###

## Call the Find Tasks script.  That's it. 
	thisDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd -P )"
	program="${thisDir}/find_tasks.py"

	python ${program}

