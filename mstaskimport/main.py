# MSTaskImport
# Copyright (C) 2024  Vaclav Koldus

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import traceback

import tornado

from mstaskimport.tasks import load_from_csv
from mstaskimport.graph_api import (
    start_authorization,
    get_token,
    post_task_list,
    post_task,
    post_checklist_item,
)

tasks_to_import = None
task_group = None
token = None
shutdown_event = asyncio.Event()


class HandlerThatShutsdownOnError(tornado.web.RequestHandler):
    def write_error(self, status_code: int, **kwargs) -> None:
        self.write(
            "Unexpected error happened during processing your data or communicating with MS servers.<br /><br />"
        )

        if "exc_info" in kwargs:
            _, e, _ = kwargs["exc_info"]
            self.write(str(e))
            self.write("<br /><br />")

            # for line in traceback.format_exception(e):
            #     self.write(line + "<br />")

        shutdown_event.set()


class TokenHandler(HandlerThatShutsdownOnError):
    def get(self):
        global token

        code = self.get_argument("code", None)
        error = self.get_argument("error", None)

        if code:
            token = get_token(code)
            self.redirect("/import")
        else:
            self.write("<title>MS Task Import</title>")
            self.write(
                f"Sorry, no code returned from MS gateway, cannot continue and shutting down. Reason: '{error}'"
            )
            shutdown_event.set()


class ImportHandler(HandlerThatShutsdownOnError):
    def get(self):
        global token, tasks_to_import, task_group

        task_list_id = post_task_list(token=token, name=task_group)

        self.write("<title>MS Task Import</title>")
        self.write("Import in progress...")
        self.flush()

        last_added_task_id = None
        for task in reversed(tasks_to_import):
            last_added_task_id = post_task(
                token=token,
                list_id=task_list_id,
                name=task.name,
                description=task.description,
            )

            for child in task.children:
                if last_added_task_id is not None:
                    post_checklist_item(
                        token=token,
                        list_id=task_list_id,
                        task_id=last_added_task_id,
                        name=(
                            child.name
                            if not child.description
                            else child.name + " " + child.description
                        ),
                    )

        self.write("DONE<br />Thank you for importing with us :) ")
        shutdown_event.set()


async def async_main(file_to_import):
    global tasks_to_import, task_group
    tasks_to_import = load_from_csv(file_to_import)

    task_group = Path(file_to_import).stem

    if len(tasks_to_import) < 1:
        print(f"No tasks found in file '{file_to_import}'.")
        return -1

    app = tornado.web.Application(
        [
            (r"/token", TokenHandler),
            (r"/import", ImportHandler),
        ]
    )
    app.listen(8000)

    start_authorization()

    await shutdown_event.wait()


def main():
    root = tk.Tk()
    root.withdraw()

    import_file_path = filedialog.askopenfilename()
    import_file_path = import_file_path.strip()

    if import_file_path:
        asyncio.run(async_main(file_to_import=import_file_path))


if __name__ == "__main__":
    main()
