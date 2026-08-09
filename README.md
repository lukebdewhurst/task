# Task tracker

Manage your tasks directly from the command line! Data is stored in JSON
format in the programs working directory.

This is a [Python](https://www.python.org/) implementation of the
[Task Tracker project on roadmap.sh](https://roadmap.sh/projects/task-tracker).

## Prerequisites

- [Python 3.14+](https://www.python.org/downloads/) *Older versions may work, 
but I haven't tested them.*

## Usage

```bash
# First, lets print the help message
$ py task.py -h
usage: task.py [-h] {add,remove,update,mark-in-progress,mark-done,list} ...

positional arguments:
  {add,remove,update,mark-in-progress,mark-done,list}

options:
  -h, --help            show this help message and exit

# Now lets create our first task
$ py task.py add "Seek the Holy Grail"
Created task of ID 0

# And now another task
$ py task.py add "Calculate the air-speed velocity of an unladen swallow"
Created task of ID 1

# An African or a Eurpean swallow? Lets update the description
$ py task.py update 1 "Calculate the air-speed velocity of an unladen African swallow"

# Let our quest for the Holy Grail begin.
$ py task.py mark-in-progress 0

# Another task cropped up
$ py task.py add "Find a shrubbery"
Created task of ID 2

# Mark it as done
$ py task.py mark-done 2

# Where are we. Lets list the tasks
$ py task.py list
Task 0: Seek the Holy Grail
| Status: in-progress
| Created At: 2026-08-09T13:15:29.054796
| Updated At: 2026-08-09T13:15:29.054796
*
Task 1: Calculate the air-speed velocity of an unladen African swallow
| Status: todo
| Created At: 2026-08-09T13:15:51.195708
| Updated At: 2026-08-09T13:15:51.195708
*
Task 2: Find a shrubbery
| Status: done
| Created At: 2026-08-09T13:16:42.600767
| Updated At: 2026-08-09T13:16:42.600767
*

# We can optionally filter them by status
$ py task.py list in-progress
Task 0: Seek the Holy Grail
| Created At: 2026-08-09T13:15:29.054796
| Updated At: 2026-08-09T13:15:29.054796
*

# And we can remove tasks at any point
$ py task.py remove 2

```
