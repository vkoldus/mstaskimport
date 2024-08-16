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

import csv
from dataclasses import dataclass


@dataclass
class Task:
    name: str
    description: str
    children: list


def load_from_csv(file_name: str) -> list[Task]:
    def validate_header(header):
        if header[0] != "TYPE":
            raise ValueError("Unrecognized csv format. First row should be 'TYPE'.")

        if header[1] != "CONTENT":
            raise ValueError("Unrecognized csv format. Second row should be 'CONTENT'.")

        if header[2] != "DESCRIPTION":
            raise ValueError(
                "Unrecognized csv format. Third row should be 'DESCRIPTION'."
            )

        if header[4] != "INDENT":
            raise ValueError("Unrecognized csv format. Fifth row should be 'INDENT'.")

    tasks: list[Task] = []
    min_level = None
    max_level = None
    with open(file_name, mode="rt", encoding="utf-8-sig") as csvfile:
        r = csv.reader(csvfile, delimiter=",", quotechar='"')

        for i, row in enumerate(r):
            if i == 0:
                validate_header(row)
            else:
                if row[0] == "task":
                    level = int(row[4])
                    if min_level is None or level < min_level:
                        min_level = level

                    if max_level is None or level > max_level:
                        max_level = level

                    if level == 1:
                        tasks.append(Task(name=row[1], description=row[2], children=[]))
                    elif level == 2 and len(tasks) > 0:
                        tasks[-1].children.append(
                            Task(name=row[1], description=row[2], children=[])
                        )

                elif row[0] == "":
                    pass
                else:
                    raise ValueError(f"Unknown record type '{row[0]}'")

    if min_level != 1:
        raise ValueError(f"Unexpected minimal task level '{min_level}'.")

    if max_level not in [1, 2]:
        raise ValueError(f"Unexpected maximal task level '{max_level}'.")

    return tasks
