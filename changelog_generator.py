import json
import requests
import dateutil.parser as parser
import datetime
import sys
import os
import time

project = sys.argv[1]
database_id = sys.argv[2]
block_id = sys.argv[3]
secret = sys.argv[4]

version_file = "C:\\Users\\Jenkins\\AppData\\Local\\Jenkins\\.jenkins\\versions\\{}_current_version.txt".format(project)
f_version = open(version_file, "r")
project_version = "V{}".format(f_version.read())
f_version.close()

headers = {
    "Notion-Version": "2022-02-22",
    "Content-Type": "application/json",
    "Authorization": secret
}

f = open("C:\\Users\\Jenkins\\AppData\\Local\\Jenkins\\.jenkins\\workspace\\{}\\git_commits.txt".format(project), "r")

class Commit: 
    def __init__(self, hash, change, message, info, date): 
        self.hash = hash 
        self.change = change
        self.message = message
        self.info = info
        self.date = date

features_list = []
changes_list = []
fixes_list = []

for x in f:
    commit_elements = x.split(";")
    commit_extract = commit_elements[1].split(":")
    commit_message = commit_extract[1].split("\\n")

    hash = commit_elements[0]
    change = commit_extract[0]
    message = commit_message[0].strip()

    message_description = ""
    if len(commit_message) > 1:
        message_description = commit_message[1].strip()

    date = commit_elements[2]

    match commit_extract[0]:
        case 'add':
            changes_list.append(Commit(hash=hash, change=change, message=message, info=message_description, date=date))
        case 'edit':
            changes_list.append(Commit(hash=hash, change=change, message=message, info=message_description, date=date))
        case 'feat':
            features_list.append(Commit(hash=hash, change=change, message=message, info=message_description, date=date))
        case 'fix':
            fixes_list.append(Commit(hash=hash, change=change, message=message, info=message_description, date=date))
        case _:
            continue

    message = {
        "title": [{
            "text": {
                "content": message.capitalize()
            }
        }]
    }
    type = { "select": { "name": change.capitalize() } }
    version = { "select": { "name": project_version } }
    date = { "date": { "start": parser.parse(date).isoformat() }  }
    properties = { "Change": message, "Type": type, "Version": version, "Date": date }

    data_set = {"parent": {"database_id": database_id}, "properties": properties}


    # Send Data to Notion
    json_dump = json.dumps(data_set)

    url = 'https://api.notion.com/v1/pages'
    
    print(requests.post(url, data = json_dump, headers = headers).text)

    time.sleep(1)

f.close()

def buildChangeList(title, list, appender):
    if len(list) == 0: return

    changes = {
        "type": "heading_3",
        "heading_3": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": title.capitalize()
                }
            }]
        }
    }
    appender.append(changes)

    divider = {
        "type": "divider",
        "divider": {}
    }
    appender.append(divider)

    for change in list:
        todo_children = []

        if change.info != "":
            additional_info = {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "annotations": {
                            "italic": True
                        },
                        "text": {
                            "content": change.info.capitalize()
                        }
                    }]
                }
            }
            todo_children.append(additional_info)

        todo_children.append({
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "annotations": {
                        "italic": True,
                        "color": "red"
                    },
                    "text": {
                        "content": "({}) - {}".format(change.hash, change.date)
                    }
                }]
            }
        })

        change_set = {
            "type": "to_do",
            "to_do": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": change.message.capitalize()
                    }
                }],
                "checked": False,
                "children": todo_children
            }
        }
        appender.append(change_set)

today = datetime.date.today()

changelog_array = []

version_text = {
  "type": "heading_2",
  "heading_2": {
    "rich_text": [{
      "type": "text",
      "text": {
        "content": project_version
      }
    }]
  }
}

total_changes = {
    "type": "paragraph",
    "paragraph": {
        "rich_text": [{
            "type": "text",
            "annotations": {
                "italic": True,
                "color": "orange"
            },
            "text": {
                "content": "{} new Features, {} Fixes and {} Changes".format(len(features_list), len(fixes_list), len(changes_list))
            }
        }]
    }
}

divider = {
    "type": "divider",
    "divider": {}
}

buildChangeList("Features", features_list, changelog_array)
buildChangeList("Bug Fixes", fixes_list, changelog_array)
buildChangeList("Changes", changes_list, changelog_array)

changelog = {"children": [
    divider,
    version_text,
    total_changes,
    {
        "type": "toggle",
        "toggle": {
            "rich_text": [{
                "type": "text",
                "annotations": {
                    "color": "blue"
                },
                "text": {
                    "content": "{} - {}".format(project_version, today.strftime("%b %d, %Y"))
                }
            }],
            "children": changelog_array
        }
    }]
}

json_dump = json.dumps(changelog)
url = "https://api.notion.com/v1/blocks/{}/children".format(block_id)
print(requests.patch(url, data = json_dump, headers = headers).text)