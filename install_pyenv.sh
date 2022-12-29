###
### To support Mac installations
###
### Installs pyenv and pyenv-virtualenv as described here:  https://realpython.com/intro-to-pyenv/
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

## First, see that brew is installed.
	whichBrew=$(which brew)
	if [[ -z "${whichBrew}" ]] 
	then
		echo "Brew doesn't seem to be installed.  We'll install it now.  You'll probably be prompted for sudo password."
		echo "If it makes you sleep better, please inspect the script install_homebrew.sh as well as https://brew.sh/"

		# Call install_hombrew.sh which does just that.
		docmd "source "${thisDir}"/install_homebrew.sh"
	fi

## With brew installed, use it to install pyenv and pyenv-virtualenv

	## According to https://realpython.com/intro-to-pyenv/#build-dependencies, we need to install some other OS-specific dependencies

		## Install Dependencies for Mac
		## As of 2022-12-28, the dependencies below were what were listed on the site linked above.  If that's since changed, update this script
		docmd "brew install openssl readline sqlite3 xz zlib"

	## With dependencies above installed, we can install pyenv.  
	## The command below comes straight from https://realpython.com/intro-to-pyenv/#using-the-pyenv-installer
	## As of, 2022-12-28 that documentation indicates that it will install the following:
		## pyenv: The actual pyenv application
		## pyenv-virtualenv: Plugin for pyenv and virtual environments
		## pyenv-update: Plugin for updating pyenv
		## pyenv-doctor: Plugin to verify that pyenv and build dependencies are installed
		## pyenv-which-ext: Plugin to automatically lookup system commands

		docmd "curl https://pyenv.run | bash"

## Handle path stuff.  There's an important manual step printed below

	## Export the path as described below, which will only last for the duration of this session.
		docmd "export PATH=$HOME/.pyenv/bin:$PATH"
		docmd "eval $(pyenv init -)"
		docmd "eval $(pyenv virtualenv-init -)"
		echo "The current value of PATH is below"
		echo "$PATH"
		echo ""

	## Print some helpful info about appending to the PATH environment
		echo "IMPORTANT!!!!"
		echo "This script just installed pyenv for you by following the steps documented here:  https://realpython.com/intro-to-pyenv/"
		echo "There is one manual semi-step however which this script did not perform on your behalf.  See the warning section at this link:"
		echo ""
 		echo "   ----------------------------------------------------------------------------"
		echo "   --->  https://realpython.com/intro-to-pyenv/#using-the-pyenv-installer  <---"
		echo "   ----------------------------------------------------------------------------"
		echo ""
		echo "Depending on your shell, you'll want to add this snippet to your ~/.bashrc (for bash) or ~/.zshrc (for zsh) file to see that it is appended to your PATH variable"
		echo 'To inspect your PATH variable, issue this command:  echo $PATH'
		echo 'To inspect which shell you are using, issue this command: echo $SHELL'
		echo "------------------------------------------"
		echo '   export PATH="$HOME/.pyenv/bin:$PATH"'
		echo '   eval "$(pyenv init -)"'
		echo '   eval "$(pyenv virtualenv-init -)"'
		echo "------------------------------------------"

	## A bit of kludge to help other scripts that call this one.  We won't rely on the user performing the steps above
	# eval "$(pyenv init -)"  
	# eval "$(pyenv virtualenv-init -)"

	