# Use Case
If you want to be able to create To-Do items in markdown syntax in your note files (e.g. Notes created with [Obsidian](https://obsidian.md/)), but have those materialize in [Todoist](https://todoist.com/) then this package is for you.

In other words:  Type away, making your notes fast an furiously.  When a To-do item pops into your mind, no need to switch apps, just make your To-do item in your markdown file and stay in the zone.

After trying it out, if you feel the urge, you can [Buy Me a Coffee](https://www.buymeacoffee.com/areese801) ☕️ ☕️ ☕️

### Live Demo Video
If you're a visual person, you can see this tool in action, [here on YouTube](https://www.youtube.com/watch?v=75H1IU0_tHo)

# Why would I want to use this utility?
- Because notes kept in [Markdown](https://www.markdownguide.org/basic-syntax/) are very portable.  Since they're plain text, they're compatible with a wide variety of tools.
	- This author's favorite tool is [Obsidian](https://obsidian.md/), but you're not limited to any one tool
- Because while To-Do items in Markdown are nice, there's no denying the power of [Todoist](https://todoist.com/).  (Scheduling, Reminders, Tagging, Delegation, etc, etc)

# What this tool is and what it is Not

### This tool is not a copy of [obsidian-todoist-plugin](https://github.com/jamiebrynes7/obsidian-todoist-plugin)

I've tried out the popular [obsidian-todoist-plugin](https://github.com/jamiebrynes7/obsidian-todoist-plugin), by [jamiebrynes7](https://github.com/jamiebrynes7) which I think is really great.  Markdown Todoist is slightly different however, in that it's more of a Batch Load of parsed tasks rather than a view into todoist Views.  I think these tools probably complement each other for different use cases.

### This tool is not an Obsidian Plugin, for now.  Perhaps never.
This tool is **Not** an [Obsidian Plugin](https://help.obsidian.md/Advanced+topics/Community+plugins).  The Primary reason for this is that [the original author](https://github.com/areese801) is better with Python than Javascript.  The original intention was to get things working with Python, as described throughout the rest of this document, then translate all of that into a "Version 2" in the form of an Obsidian plugin.

At this point, that may or may not happen.  Reason being that it could be argued that this tool is better off as a standalone code package and that the lack of tight integration with Obsidian is a feature ~~, not a bug~~ because it allows the tool to work with arbitrary Markdown files anywhere on the file system and also makes automation easy to implement (See Automation section below), which might be harder to do (or impossible?  ... I haven't looked closely enough) as an Obsidian Plugin

### This tool is basic when it comes to To-Do creation
For now, there are no bells and whistles when it comes to Migrating tasks into Todoist.  There is no (intentional) handling for [Projects](https://todoist.com/help/articles/introduction-to-projects), [Labels](https://todoist.com/help/articles/introduction-to-labels), [Priorities](https://todoist.com/help/articles/introduction-to-priorities).  Todoist itself might gracefully handle some of these things based on how the task is worded, but there are no guarantees.

Today, this tool will simply shunt To-Do tasks into your [Default Project](https://todoist.com/help/articles/whats-the-difference-between-the-inbox-and-a-project) (.e.g Inbox), with "Today" as the Due Date so that you might go on to augment these tasks with Labels and Comments, change the due date, assign to a project, etc.

The notion comes from the [GTD Method](https://todoist.com/productivity-methods/getting-things-done).

# How does this tool work?
At a high level, here's what happens:

1. When invoked, the tool traverses a directory (e.g. Obsidian Vault Directory) looking for Markdown files with a `.md` file extension.
2. These files are inspected for *Incomplete* To-Do items using regular expression pattern matching matching looking for To-Do's that look like:  `- [ ] Buy Milk`
3. Any To-Do items are "migrated" to Todoist
	- There is a basic check on file timestamp to try to ensure that To-Do items that are still being typed out aren't migrated into Todoist prematurely.
	- There is a basic check to try to avoid edge cases where a to-do with the same wording in different places would be created in Todoist more than once
4. Migrated To-Do items from `.md` files are 'crossed out' in the markdown file with a link to the corresponding task in Todoist to denote they've been migrated
5. Migrated To-Do items created in Todoist will contain the Task description as well as an [Obsidian URI](https://help.obsidian.md/Advanced+topics/Using+obsidian+URI) that points back to the file the To-Do was parsed out of
	- This linkage may be imperfect, especially if the file is moved or renamed.
	- However, in testing, basic file moves within Obsidian did not break the functionality


# Compatibility
This tool was created on a Mac using Python3 (version 3.11).  It was tested on that Mac and worked fine there.  I would expect that this code work on Windows, but there may be some minor bugs as I didn't test for Windows.  If you care to do so and encounter an issue, please get in touch with [Adam Reese](https://github.com/areese801) and/or fix it yourself and create a pull request.

# Prerequisites and Dependencies
- Python3 (This tool was originally developed and tested with Python 3.11)
- A Todoist Account with Access to the [API](https://developer.todoist.com/guides/#developing-with-todoist)
	- I believe the API is available to all [Pricing Tiers](https://todoist.com/pricing) of Todoist as of this writing (2022-12-20)
- The package uses [todoist-api-python](https://pypi.org/project/todoist-api-python/) under the hood so that needs to be installed and available to whichever Python3 installation or virtual environment you use
	- You may find [make_env.sh](https://gist.github.com/areese801/e51773aefa16a826459aba075c852630) useful for setting up a Python Virtual Environment, but YMMV

# Setup

### Get the latest version of the code
Clone or Download and Extract the code from the repository to your preferred destination. `~/scripts` is a good spot if you're not sure where else to put it.

### Set up Python Virtual Environment or Manually Install Required Packages
The `make_pyenv_venv.sh` script does it's best to bootstrap a Python Virtual Environment using `pyenv virtualenv` (more on that [here](https://realpython.com/intro-to-pyenv/#virtual-environments-and-pyenv)) with the requirements from `requirements.txt` installed.  You can run this script if you'd like to use that sort of setup.

If you'd like to avoid pyenv some reason, all that is really needed at the end of the day is a Python installation with [todoist-api-python](https://pypi.org/project/todoist-api-python/) installed so this command might be all you need:

```bash
pip install -U -r requirements.txt
```


### Configure config files
There are 2 config files you'll need to create under the `config` folder:
- `config.json` which contains config for the program itself
- `todoist_api_config.json` which contains your API token (Sensitive.  Treat it as such)

#### Configure `config.json`
- As of this writing (2022-12-20), the only thing to configure in this file is the base directory (for example:  `~/Obsidian`) where markdown files and subdirectories with more markdown files can be found.
- See [config_TEMPLATE.json](https://github.com/areese801/markdown_todoist/blob/main/config/config_TEMPLATE.json) to understand how the file should be formatted
- Make a copy of the file and remove the comments to make it valid JSON

#### Configure `todoist_api_config.json`
- You'll have to create a configuration file with your Todoist API token in it.
	- See [todoist_api_config_TEMPLATE.json](https://github.com/areese801/markdown_todoist/blob/main/config/todoist_api_config_TEMPLATE.json "todoist_api_config_TEMPLATE.json") to understand how that should be formatted.
	- Take heed to the notes at the top of that file regarding your API token
	- Make a copy of the file and remove the comments to make it valid JSON.
	- Enter your Todoist API Token
		- To find this in Todoist:  `Settings > Integrations > Developer > API Token`

# Using the tool (Manually)

### Just to see To-Do items
If you just want to print a list of your To-Do's but not "Migrate" them, as described above you can use `find_tasks.py` like this:
```bash
python find_tasks.py
```

Alternatively, you can use the wrapper script that's intended to place nicely with `pyenv`
```bash
./find.sh
```

### To Migrate To-Do items into Todoist
To migrate To-Do items as described in the **How does this tool work?** section above, use `migrate_tasks.py` like this:

```bash
python migrate_tasks.py
```

Alternatively, you can use the wrapper script that's intended to place nicely with `pyenv`
```bash
./migrate.sh
```

# Automation

### On MacOS or Linux
You can automate `migrate_tasks.py` on MacOS (Or anything **\*nix**) using a `cron` entry.  This set up is out of scope to describe here, but for the unfamiliar [here is a good place to start](https://www.howtogeek.com/101288/how-to-schedule-tasks-on-linux-an-introduction-to-crontab-files/).  As an example, you might make a `crontab` entry like this:

```bash
# Parse to-do items out of Markdown files and create corresponding to-do's in Todoist
0 */1 * * 1-5 cd ~/path/to/wherever/you/have/this/script && python migrate_tasks.py > /tmp/migrate_tasks.log 2>&1
```

You can use [this website](https://crontab.guru/) to help generate and validate your crontab schedules

### On Windows
As mentioned above, this script hasn't been tested on Windows, but should work without requiring too much (or any) fixing.  On Windows, instead of cron, you'd want to use the [Windows Task Scheduler](https://www.windowscentral.com/how-create-automated-task-using-task-scheduler-windows-10), the set up for which is out of scope to describe here.

# About synchronization

### Synchronization should just work
If you've set up any kind of Synchronization for your Markdown notes ([Obsidian Sync](https://obsidian.md/sync), [Dropbox](https://www.dropbox.com/), [Syncthing](https://syncthing.net/), etc), this tool should, in-theory, work without any issue, but please let [Adam Reese](https://github.com/areese801) know and/or fix it yourself and create a pull request if you encounter any issues.

This was tested with Obsidian Sync and it worked fine.

### Ok, but why "should" it just work?
When a task is "migrated", this tool modifies the markdown file that that task was parsed from on-the-fly.

So a task that looks like this, pre-migration:

![](./_resources/Pasted%20image%2020221220110643.png)

Will end up looking like this, post-migration:

![](./_resources/Pasted%20image%2020221220110655.png)

Visually, in Obsidian the syntax from the screen prints above renders like this, before and after
Before:

![](./_resources/Pasted%20image%2020221220110918.png)

After:

![](./_resources/Pasted%20image%2020221220110807.png)

Here's what the generated task in Todoist Looks like:

![](./_resources/Pasted%20image%2020221220110455.png)

# Did you save time or money by using this tool? ⏱️ 💰 ⏱️ 💰 

If so, you can [Buy Me a Coffee](https://www.buymeacoffee.com/areese801) 

☕️ ☕️ ☕️
