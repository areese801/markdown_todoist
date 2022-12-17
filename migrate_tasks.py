"""
Code having to do with migrating tasks read from Markdown files into Todoist


Rather than having to try to come up with some tricky way to sync and keep track
of (potentially renamed) files across multiple machines, I decided to
build functionality to 'migrate' tasks into todoist on the fly with a standard
convention to denote those having been migrated.  This approach allows me to
avoid duplications, forget about tracking file names and locations, and
take advantage of the very nature of sync.
"""
import todoist
from find_tasks import find_tasks
import re
from todoist import get_api_token
from todoist import get_todoist_tasks

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

		# TODO:  Ship the task into todoist here
		# Todo: Check the last modified stamp on the file.  Maybe ignore modified within the last minute
		#   Idea is to avoid making tasks in todoist that are currently being typed out

		todoist_task_url = "http://foo.bar"  #TODO:  Replace this kludge with something real

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


		# TODO:  After buttoning up the piece that would create the todoist task
		# Modify the markdown file here.
		# Make it create a .backup file with the original contents and a datestamp


if __name__ == '__main__':
	data = migrate_tasks()
	print("!")

