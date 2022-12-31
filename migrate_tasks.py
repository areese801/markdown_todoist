"""
Code having to do with migrating tasks read from Markdown files into Todoist


Rather than having to try to come up with some tricky way to sync and keep track
of (potentially renamed) files across multiple machines, I decided to
build functionality to 'migrate' tasks into todoist on the fly with a standard
convention to denote those having been migrated.  This approach allows me to
avoid duplications, forget about tracking file names and locations, and
take advantage of the very nature of sync.
"""

import os.path
import sys
import shutil

import todoist
from find_tasks import find_tasks
from config import _read_base_dir_from_config
import re
import datetime
from datetime import timezone
from hashing import make_task_hash


def migrate_tasks(parent_directory:str = '~/Obsidian'):
	"""
	Migrates open tasks into todoist by creating a task in todoist then modifying the markdown
	File / line from where the task was encountered
	"""

	# TODO:  Read the parent directory path out of a config file

	tasks_from_markdown_files = find_tasks(parent_directory=parent_directory)

	# Exit if there's nothing to do
	if not tasks_from_markdown_files:
		# Nothing to do
		print(f"There are no tasks to migrate.  Call to find_tasks results in: {str(tasks_from_markdown_files)}")
		return

	# Get the current list of tasks from the todoist API  This will help ensure we don't duplicate tasks
	todoist_api_token = todoist.get_api_token()
	todoist_tasks = todoist.get_todoist_tasks(todoist_api_token=todoist_api_token)

	recently_modified_files = [] #Tracks files that were modified by current invocation.  To not-skip due to modify time.


	for task_dict in tasks_from_markdown_files:

		"""
		Check the last modified time of the file.  If it's less than X seconds ago, don't bother with it
		The idea here is to not ship incomplete to-do items that the user might still by typing out into to
		Todoist prematurely.  For example, if this program was scheduled on a cron job
		"""

		markdown_file_name = task_dict['file_name']

		# take note of the current timestamp in UTC
		right_now = datetime.datetime.now(timezone.utc)
		right_now_utc_timestamp = right_now.timestamp()

		# take note of the timestamp on the file
		file_last_modified_timestamp = os.path.getmtime(markdown_file_name)

		time_diff_sec = right_now_utc_timestamp - file_last_modified_timestamp
		if file_last_modified_timestamp > right_now_utc_timestamp or time_diff_sec < 60:
			# TODO:  Read this seconds threshold out of a config file and allow the user bypass this behavior entirely
			# File is too new.  Skip it for now
			if markdown_file_name not in recently_modified_files:
				# We might have just modified a file due to another to-do item, changing its TS.
				# It's ok to modify again in such cases.
				continue

		"""
		For good measure, bump the list of existing tasks from todoist up against that which is in scope right now
		"""
		markdown_task_md5_hash = task_dict['task_md5_hash']
		matching_task_in_todoist = False
		for tdt in todoist_tasks:
			todoist_task_md5_hash = make_task_hash(task_description=tdt.content)
			if todoist_task_md5_hash == markdown_task_md5_hash:
				matching_task_in_todoist = True
				break

		if matching_task_in_todoist is True:
			# TODO:  Read behavior for this out of a config file to enable or disable
			print(f"The task '{task_dict['task']}' parsed from the markdown file '{markdown_file_name}' seems to be a "
			      f"duplicate of a task that already exists in todoist, '{tdt.content}'.  "
			      f"As such, it will be skipped over.", file=sys.stderr)
			continue

		"""
		Make the task in todoist.  This is the moment we've been waiting for!
		"""
		task_content = task_dict['task']
		original_file_name = os.path.basename(markdown_file_name)
		task_description = f"Migrated from [{original_file_name}]({task_dict['obsidian_uri']}). " \
		               f"(Link may break if file was renamed or moved.)"  #TODO:  Make a post on message board to try to uinderstand this behavior


		new_todoist_task = todoist.create_task(todoist_api_token=todoist_api_token,
		                                       task_content=task_content,
		                                       task_description=task_description)
		if new_todoist_task is Exception:
			raise new_todoist_task
		else:
			todoist_task_url = new_todoist_task.url


		"""
		Construct a markdown string to replace the original with
		"""

		# Handle the markdown part of the task:  '- [ ] "
		markdown_todo_regex_pattern = "(^\s*- \[)( )(\]\s*)"
		arrow_character = "→" # Used to denote a 'migrated' task.  In markdown any char other than ' ' will signify complete.
		task_markdown_part = task_dict['markdown_part']  # This looks like:  '- [ ]'
		markdown_todo_regex_match = re.match(string=task_markdown_part, pattern=markdown_todo_regex_pattern)
		re_1 = markdown_todo_regex_match.group(1) # Looks like:  - [
		re_3 = markdown_todo_regex_match.group(3).rstrip() # Looks like:  ].  The empty space would be in group 2
		new_task_markdown_part = f"{re_1}{arrow_character}{re_3} "

		# Handle the part of the string that links to the new task in todoist
		todoist_link_part = f" [(This Task Migrated to Todoist)]({todoist_task_url})"

		# Construct a complete line of text to replace the original to-do that was parsed from the file
		replacement_todo_string = f"{new_task_markdown_part}~~{task_dict['task']}~~{todoist_link_part}"


		#TODO:  Drop these helper messages.  Or don't
		print("\nThe program will find and replace the following:")
		print(f"\tWithin the file '{markdown_file_name}'")
		print(f"\tThis string will be sought:            {task_dict['original_string']}")
		print(f"\tWhich will be replaced by the string:  {replacement_todo_string}")

		# Create a backup copy of the file before modifying it
		#TODO:  Probably safe to comment this out or disable via config after having used this tool for a while
		# backup_file_name = f"{markdown_file_name}.{right_now.strftime('%Y-%m-%d')}.bak"
		# if not os.path.isfile(backup_file_name):
		# 	shutil.copy(src=markdown_file_name, dst=backup_file_name)
		# 	print(f"Created a backup file before modifying to-do item in place in the original.  Backup file name is:  '{backup_file_name}'")
		# else:
		# 	print(f"A backup file '{backup_file_name}' already exists.  Will not create another backup file")

		"""
		Replace the original line in the file with a to-do item on it with the new field that 
		show's it's been migrated to todoist
		"""
		# Read the lines of the file first
		with open(markdown_file_name, 'r') as f:
			lines = f.readlines()

		# Modify the lines
		new_lines = []
		for line in lines:
			if line.strip().startswith(task_dict['original_string']):
				new_lines.append(replacement_todo_string)
			else:
				new_lines.append(line.rstrip())  # We don't want trailing \n char or we'll get doubles when we join
		new_file_data = "\n".join(new_lines)  #TODO:  Might need to do a check here to place nicely with windows

		# Replace the lines of the original file with the new lines
		with open(markdown_file_name, 'w') as f:
			f.write(new_file_data)
			f.close()
		recently_modified_files.append(markdown_file_name) # Helps us merge many tasks from the same file in without TS check


		# To Do:  Cross out the todo in the markdown file
		# Pick back up here next time
		# TODO:  After buttoning up the piece that would create the todoist task
		# Modify the markdown file here.
		# Make it create a .backup file with the original contents and a datestamp


if __name__ == '__main__':

	# Resolve the path to the vault.  If it's not passed in, get it from the config file
	args = sys.argv

	if len(args) >= 2:
		base_dir = args[1]
	else:
		base_dir = _read_base_dir_from_config()

	migrate_tasks(parent_directory=base_dir)




