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

import json
import requests
import webbrowser

CLIENT_ID = "REDACTED"
SCOPE = "Tasks.ReadWrite"
OAUTH_API_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0"
REDIRECT_URI = "http://127.0.0.1:8000/token"
API_URI = "https://graph.microsoft.com/v1.0/me/todo"


def start_authorization():
    webbrowser.open(
        f"{OAUTH_API_URL}/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&response_mode=query&scope={SCOPE}"
    )


def get_token(code):
    response = requests.post(
        f"{OAUTH_API_URL}/token",
        data={
            "code": code,
            "client_id": CLIENT_ID,
            "scope": SCOPE,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    )
    r = response.json()

    if r.get("token_type") != "Bearer":
        raise ValueError(f"Token not received. {r.get('error_description')}")

    return r["access_token"]


def get_task_lists(*, token):
    response = requests.get(
        API_URI + "/lists", headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()


def post_task_list(*, token, name):
    response = requests.post(
        API_URI + "/lists",
        data=json.dumps({"displayName": name}),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "Application/JSON",
        },
    )

    r = response.json()
    if "id" in r:
        return r["id"]
    else:
        raise ValueError("Could not create task list." + str(r))


def post_task(*, token, list_id, name, description):
    response = requests.post(
        API_URI + f"/lists/{list_id}/tasks",
        data=json.dumps(
            {"title": name, "body": {"contentType": "text", "content": description}}
        ),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "Application/JSON",
        },
    )

    r = response.json()
    if "id" in r:
        return r["id"]
    else:
        raise ValueError("Could not create task. " + str(r))


def post_checklist_item(*, token, list_id, task_id, name):
    response = requests.post(
        API_URI + f"/lists/{list_id}/tasks/{task_id}/checklistItems",
        data=json.dumps({"displayName": name}),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "Application/JSON",
        },
    )

    r = response.json()
    if "id" in r:
        return r["id"]
    else:
        raise ValueError("Could not create task. " + str(r))
