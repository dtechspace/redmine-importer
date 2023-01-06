"""Imports a Redmine project from an Assembla space using the populated settings
in the settings.ini file in the same directory.

© Copyright 2020, D-Tech, LLC, All Rights Reserved. 
Version: 0.5 (initial version), 01/05/2023
License: The use of this software program is subject to the Redmine-Importer
license terms and conditions as defined in the LICENSE file.
Disclaimer: This software is provided "AS IS" without warrantees.  
D-Tech, LLC has no obligation to provide any maintenence, update 
or support for this software.  Under no circumstances shall D-Tech,  
LLC be liable to any parties for direct, indirect, special, incidental,
or consequential damages, arising out of the use of this software
and related data and documentation.
"""

from converter import md
import configparser
from assembla_download import * 
from redminelib import Redmine
import redminelib

config = configparser.ConfigParser()
config.read('settings.ini')
REDMINE_API_KEY = config['Redmine Keys']['REDMINE_API_KEY']
REDMINE_URL = config['Redmine Keys']['REDMINE_URL']
REDMINE_PROJECT = config['Redmine Keys']['REDMINE_PROJECT']

redmine = Redmine(REDMINE_URL, key=REDMINE_API_KEY)
project = redmine.project.get(REDMINE_PROJECT)

def wiki_page_upload():
    """
    Imports all wiki pages from an Assembla space to a Redmine project.
    """
    page_queue = get_assembla_pages()
    pq_dict = {p['id'] : p['page_name'] for p in page_queue}
    has_seen = set()

    counter = 0
    while page_queue: 
        wp = page_queue.pop(0)
        if (wp['parent_id'] and wp['parent_id'] not in has_seen):
            page_queue.append(wp)
            continue
        
        print(counter, wp['page_name'])
        counter += 1
        has_seen.add(wp['id'])
        
        uploads = []
        markdown, uploads = md(wp['contents'], uploads)
        replacements = (('&nbsp;', ' '), ('&lt;', '<'), ('&gt;', '>'), 
                        ('&quot;', '"'), ('&#39;', '\''), ('&amp;', '&'))
                    
        page_name_no_period = wp['page_name'].replace('.', '')
        page_parent = None if not wp['parent_id'] else pq_dict[wp['parent_id']]
        for r in replacements:
            markdown = markdown.replace(*r)
        try: 
            redmine.wiki_page.create(
                project_id=REDMINE_PROJECT,
                title=page_name_no_period,
                text=markdown if markdown != '' else '---',
                uploads=uploads, 
                parent_title=page_parent
            )
        except redminelib.exceptions.ValidationError as e: 
            print("Exception:", e)
            redmine.wiki_page.update(
                page_name_no_period,
                project_id=REDMINE_PROJECT,
                title=page_name_no_period,
                text=markdown if markdown != '' else '---',
                uploads=uploads, 
                parent_title=page_parent
            )
        except Exception as e:
            print(e)
            print("{} could not be uploaded; skipping for now.".format(wp['page_name']))
            continue
        
    if page_queue: 
        print("Couldn't upload the following pages:", page_queue)


def ticket_upload():
    """
    Imports all issues from an Assembla space to a Redmine project.
    """
    tickets = get_assembla_tickets()
    sid_dict = {
        'New' : 1, 
        'Accepted' : 2, 
        'Test' : 4, 
        'Fixed' : 5, 
        'Invalid' : 6, 
        'Awaiting Dependency' : 4, 
        'Discussion': 4,
        'In-Progress': 2
    }
    pid_dict = {5 : 1, 4 : 1, 3 : 2, 2 : 3, 1 : 4}
    for ticket in tickets: 
        data = ticket.data
        due_date = data['due_date'] if data['due_date'] else data['created_on'][:10]
        try:
            issue = redmine.issue.create(
                project_id=REDMINE_PROJECT,
                subject=data['summary'],
                description=data['description'],
                tracker_id=2,
                status_id=sid_dict.get(data['status'], 2),
                priority_id=pid_dict[data['priority']],
                start_date=data['created_on'][:10],
                due_date=max(due_date, data['created_on'][:10])
            )
            redmine.issue.update(
                issue.id,
                project_id=REDMINE_PROJECT,
                tracker_id=2,
                status_id=sid_dict.get(data['status'], 2),
                priority_id=pid_dict[data['priority']],
            )
            for comment in ticket.comments()[::-1]: 
                if comment.data['comment']:
                    cmt, ups = assembla_to_redmine_markdown(comment.data['comment'])
                    redmine.issue.update(
                        issue.id,
                        tracker_id=2,
                        status_id=sid_dict.get(data['status'], 2),
                        priority_id=pid_dict[data['priority']],
                        notes=cmt, 
                        uploads=ups
                    )
        except Exception as e:
            print(e)
            print("Issue {} could not be uploaded; currently skipping".format(data['summary']))
            continue

if __name__ == "__main__":
    wiki_page_upload()
    ticket_upload()
    print("Wiki Pages and Tickets done uploading.")