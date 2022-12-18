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

import todoist
from find_tasks import find_tasks
import re
import datetime
from datetime import timezone
from parsers import make_task_hash

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

	# Get the current list of tasks from the todoist API  This will help ensure we don't duplicate tasks
	todoist_api_token = todoist.get_api_token()
	todoist_tasks = todoist.get_todoist_tasks(todoist_api_token=todoist_api_token)

	for task_dict in tasks_from_markdown_files:

		"""
		Check the last modified time of the file.  If it's less than X seconds ago, don't bother with it
		The idea here is to not ship incomplete to-do items that the user might still by typing out into to
		Todoist prematurely.  For example, if this program was scheduled on a cron job
		"""

		# take note of the current timestamp in UTC
		right_now_utc_timestamp = datetime.datetime.now(timezone.utc).timestamp()

		# take note of the timestamp on the file
		file_last_modified_timestamp = os.path.getmtime(task_dict['file_name'])

		time_diff_sec = right_now_utc_timestamp - file_last_modified_timestamp
		if file_last_modified_timestamp > right_now_utc_timestamp or time_diff_sec < 120:
			# TODO:  Read this seconds threshold out of a config file and allow the user bypass this behavior entirely
			# File is too new.  Skip it for now
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
			print(f"The task parsed from a markdown file '{task_dict['task']}' seems to be a duplicate of a task"
			      f" that already exists in todoist, '{tdt.content}'.  As such, it will be skipped over.", file=sys.stderr)
			continue

		"""
		Make the task in todoist.  This is the moment we've been waiting for!
		"""
		task_content = task_dict['task']
		original_file_name = os.path.basename(task_dict['file_name'])
		task_description = f"This todo item was parsed from [{original_file_name}]({task_dict['obsidian_uri']}). " \
		               f"Note that this link may be broken if the file was renamed or moved."


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
		print(f"\tWithin the file '{task_dict['file_name']}'")
		print(f"\tThis string will be sought:            {task_dict['original_string']}")
		print(f"\tWhich will be replaced by the string:  {replacement_todo_string}")
		print("!")


		# To Do:  Cross out the todo in the markdown file
		# Pick back up here next time
		# TODO:  After buttoning up the piece that would create the todoist task
		# Modify the markdown file here.
		# Make it create a .backup file with the original contents and a datestamp


if __name__ == '__main__':
	data = migrate_tasks()
	print("!")

