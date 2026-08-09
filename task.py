from dataclasses import dataclass, fields, replace
from datetime import datetime
from enum import Enum
from json import load, dump
from argparse import ArgumentParser, Namespace
from pathlib import Path

class Status(Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"

@dataclass(frozen=True)
class Task:
    description: str
    status: Status
    created_at: datetime
    updated_at: datetime

    # Validate instance
    def __post_init__(self):
        if not self.description.strip():
            raise ValueError("Empty description")

    # Map Task from JSON serializable (data) dict
    @classmethod
    def from_data(cls, data: dict):
        types = {field.name: field.type for field in fields(cls)}
        for name, value in data.items():
            # Skip items not defined by Task
            if name not in types:
                del data[name]
                continue
            # Map data
            type = types[name]
            if type == Status:
                data[name] = Status(value)
            elif type == datetime:
                data[name] = datetime.fromisoformat(value)
        return cls(**data)

    # Map Task to JSON serializable (data) dict
    def to_data(self):
        pairs = []
        for name in map(lambda field: field.name, fields(self)):
            value = getattr(self, name)
            if isinstance(value, Status):
                value = value.value
            elif isinstance(value, datetime):
                value = value.isoformat()
            pairs.append((name, value))
        return dict(pairs)

def load_tasks(path: Path):
    with open(path, "r") as file:
        tasks: dict[int, Task] = {}
        data = load(file)
        if not isinstance(data, dict):
            raise ValueError("Root is not a dict")
        for k, v in data.items():
            id = None
            try:
                id = int(k)
            except ValueError as e:
                raise ValueError(f"Cannot cast task ID: {e}")
            if not isinstance(v, dict):
                raise ValueError(f"Task of ID {id} is not a dict")
            try:
                tasks[id] = Task.from_data(v)
            except Exception as e:
                raise Exception(f"Exception when mapping task of ID {id}: {e}")
        return tasks

def dump_tasks(tasks: dict[int, Task], path: Path):
    data = {id: task.to_data() for id, task in tasks.items()}
    with open(path, "w+") as file:
        dump(data, file, indent=4)

def assert_task_exists(id, tasks):
    if id not in tasks:
        raise ValueError(f"Task of ID {id} does not exist")

def handle_add(ns: Namespace):
    id = max(ns.tasks.keys()) + 1 if ns.tasks else 0
    now = datetime.now()
    ns.tasks[id] = Task(ns.description, Status.TODO, now, now)
    dump_tasks(ns.tasks, ns.path)
    print(f"Created task of ID {id}")

def handle_remove(ns: Namespace):
    assert_task_exists(ns.id, ns.tasks)
    del ns.tasks[ns.id]
    dump_tasks(ns.tasks, ns.path)

def handle_update(ns: Namespace):
    assert_task_exists(ns.id, ns.tasks)
    ns.tasks[ns.id] = replace(ns.tasks[ns.id], description=ns.description)
    dump_tasks(ns.tasks, ns.path)

def handle_mark_in_progress(ns: Namespace):
    assert_task_exists(ns.id, ns.tasks)
    ns.tasks[ns.id] = replace(ns.tasks[ns.id], status=Status.IN_PROGRESS)
    dump_tasks(ns.tasks, ns.path)

def handle_mark_done(ns: Namespace):
    assert_task_exists(ns.id, ns.tasks)
    ns.tasks[ns.id] = replace(ns.tasks[ns.id], status=Status.DONE)
    dump_tasks(ns.tasks, ns.path)

def handle_list(ns: Namespace):
    # Mask is a set of statuses to filter by. Only tasks with a status contained
    # in mask should be printed, unless the mask is empty (in which case, the
    # user didn't supply any statuses to filter by).
    # NOTE: "-" is replaced with "_" for namespace attributes, so "in-progress"
    # becomes "in_progress".
    mask = {s for s in Status if getattr(ns, s.value.replace("-", "_"))}
    for id, task in ns.tasks.items():
        if len(mask) > 0 and task.status not in mask:
            continue
        print(f"Task {id}: {task.description}")
        print(f"| Status: {task.status.value}")
        print(f"| Created At: {task.created_at.isoformat()}")
        print(f"| Updated At: {task.updated_at.isoformat()}")
        print("*")

def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(required=True)
    parser.add_argument("--file", nargs=1)

    add_parser = subparsers.add_parser("add")
    add_parser.set_defaults(handler=handle_add)
    add_parser.add_argument("description")

    remove_parser = subparsers.add_parser("remove")
    remove_parser.set_defaults(handler=handle_remove)
    remove_parser.add_argument("id", type=int)

    update_parser = subparsers.add_parser("update")
    update_parser.set_defaults(handler=handle_update)
    update_parser.add_argument("id", type=int)
    update_parser.add_argument("description")

    mark_in_progress_parser = subparsers.add_parser("mark-in-progress")
    mark_in_progress_parser.set_defaults(handler=handle_mark_in_progress)
    mark_in_progress_parser.add_argument("id", type=int)

    mark_done_parser = subparsers.add_parser("mark-done")
    mark_done_parser.set_defaults(handler=handle_mark_done)
    mark_done_parser.add_argument("id", type=int)

    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(handler=handle_list)
    for status in Status:
        list_parser.add_argument(f"--{status.value}", action="store_true")

    ns = parser.parse_args()
    ns.path = (Path(ns.file[0]).resolve() if ns.file else 
               Path(Path(__file__).parent, "task.json"))

    try:
        ns.tasks = load_tasks(ns.path)
    except OSError:
        ns.tasks = {} # Treat no file as empty file
    except Exception as e:
        print(f"Exception when loading task file: {e}")
        exit(1)

    try:
        ns.handler(ns)
    except Exception as e:
        print(f"Exception when running command: {e}")
        exit(1)

if __name__ == "__main__":
    main()
