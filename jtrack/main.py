#!/usr/bin/python
# coding=utf-8
import argparse
import sqlite3
import os
from atlassian import Jira
import sys

# Default values.
JIRA_CLOSED = ['Closed', 'Resolved']
JIRA_TYPE = "Task"
JIRA_LABELS = []

# Check if we are running this on windows platform
IS_WINDOWS = sys.platform.startswith('win')

# Console Colors
if IS_WINDOWS:
    # Windows deserves coloring too :D
    G = '\033[92m'  # green
    Y = '\033[93m'  # yellow
    B = '\033[94m'  # blue
    R = '\033[91m'  # red
    W = '\033[0m'   # white
    try:
        import win_unicode_console, colorama
        win_unicode_console.enable()
        colorama.init()
    except:
        G = Y = B = R = W = G = Y = B = R = W = ''
else:
    G = '\033[92m'  # green
    Y = '\033[93m'  # yellow
    B = '\033[94m'  # blue
    R = '\033[91m'  # red
    W = '\033[0m'   # white


def db_install(sqli_db):
    if not (os.path.isfile('./' + sqli_db)):
        db = sqlite3.connect(sqli_db)
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE jira(identifier TEXT PRIMARY KEY, jira_key TEXT)''')
        db.commit()
        db.close()
    else:
        pass


def upsert_new_identifier(identifier, jira_key):
    try:
        # Update if it exists
        cursor.execute('''UPDATE jira SET jira_key=? WHERE identifier=?''', (jira_key, identifier))
        # Insert or ignore if already exists
        cursor.execute('''INSERT OR IGNORE INTO jira(identifier, jira_key) VALUES(?,?)''', (identifier, jira_key))
        db.commit()
    except Exception as e:
        print(e)


def is_identifier_in_db(identifier):
    try:
        cursor.execute('''SELECT * from jira where identifier = ?''', (identifier,))
        if cursor.fetchall():
            return True
        else:
            return False
    except Exception as e:
        return False


def get_jira_key_by_identifier(identifier):
    try:
        cursor.execute('''SELECT jira_key FROM jira where identifier = ?''', (identifier,))
        all_rows = cursor.fetchall()
        for row in all_rows:
            return row[0]
    except Exception as e:
        print(e)
    return ""


def update_jira_db(id, jira_key):
    try:
        cursor.execute('''UPDATE jira SET jira_key = ? WHERE id = ? ''', (jira_key, id))
        db.commit()
    except Exception as e:
        print("We could not connect to {} due to following error: {}".format(jira_key, e))


# Checks if we already have an existing Jira task so we'll know if we want to update or create a new one.
def has_existing_task(identifier, jira_closed):
    if is_identifier_in_db(identifier):
        jira_key = get_jira_key_by_identifier(identifier)
        status = jira.get_issue_status(jira_key)
        # If task exists, but closed - return false.
        if status in jira_closed:
            return False
        else:
            return True
    return False


# Upsert a jira issue (wrapper for insert or update actions).
def upsert_jira(identifier, project, summary, skip_existing, jira_closed, attachment, type, description, labels):
    if has_existing_task(identifier, jira_closed):
        if skip_existing:
            print('Issue already exists and open. Skipping.')
            return False
        jira_key = get_jira_key_by_identifier(identifier)
        update_jira(jira_key, attachment)
    else:
        new_jira = create_new_jira(project, type, summary, description, labels, attachment)
        jira_key = new_jira['key']
        upsert_new_identifier(identifier, jira_key)
        print(f'Created new Jira ticket: {jira_key}. jTrack id: {identifier}')


# Create a new Jira issue.
def create_new_jira(project, type, summary, description, labels, attachment):
    new_task = jira.issue_create(fields={
        'project': {'key': project},
        'issuetype': {
            "name": type
        },
        'summary': summary,
        'labels': labels
    })

    jira_key = new_task['id']

    # Add the report as an attachment
    if attachment is not None:
        jira.add_attachment(jira_key, attachment)

    # Add description.
    if description is not None:
        desc_field = {'description': description}
        jira.update_issue_field(jira_key, desc_field)

    return new_task


# Currently onlyl support attachment addition.
# @todo Extend to support description.
def update_jira(jira_key, attachment):
    if attachment is not None:
        jira.add_attachment(jira_key, attachment)
    else:
        print('No attachment provided. Nothing to updated.')


def attachment_arg(path):
    # from os.path import exists
    if not os.path.isfile(path):
        raise ValueError  # or TypeError, or `argparse.ArgumentTypeError
    return path


def banner():
    print("""%s                                        
  ,--.,--------.                     ,--.     
  `--''--.  .--',--.--. ,--,--. ,---.|  |,-.  
  ,--.   |  |   |  .--'' ,-.  || .--'|     /  
  |  |   |  |   |  |   \ '-'  |\ `--.|  \  \  
.-'  /   `--'   `--'    `--`--' `---'`--'`--' 
'---'%s%s

              # Coded By Rotem Reiss - @2RS3C
    """ % (B, W, B))


def main(identifier, project, summary, **kwargs):
    global db
    global cursor
    global jira

    # Every tool needs a banner.
    if kwargs.get('quiet', False) is False:
        banner()

    # Jira Connection Details
    JIRA_URL = os.environ.get('JIRA_URL')
    JIRA_USER = os.environ.get('JIRA_USER')
    JIRA_PASSWORD = os.environ.get('JIRA_PASSWORD')

    jira = Jira(
        url=JIRA_URL,
        username=JIRA_USER,
        password=JIRA_PASSWORD)

    # Init DB.
    sqli_db = "jtrack.db"
    db_install(sqli_db)
    db = sqlite3.connect(sqli_db)
    cursor = db.cursor()

    # Initialize default values.
    skip_existing = kwargs.get('skip_existing', True)
    jira_closed = kwargs.get('jira_closed', JIRA_CLOSED)
    attachment = kwargs.get('attach', None)
    itype = kwargs.get('type', JIRA_TYPE)
    description = kwargs.get('desc', None)
    labels = kwargs.get('labels', JIRA_LABELS)
    upsert_jira(identifier, project, summary, skip_existing, jira_closed, attachment, itype, description, labels)

    db.close()


def interactive():
    parser = argparse.ArgumentParser(description='Creates a Jira task.')

    # Add the arguments
    parser.add_argument('-i', '--identifier', help='A system identifier for the issue.', dest='identifier',
                        required=True)
    parser.add_argument('-p', '--project', help='The project\'s name on Jira (e.g. EXAMPLE).', dest='project',
                        required=True)
    parser.add_argument('-s', '--summary', help='Value for the summary field.', dest='summary', required=True)
    parser.add_argument('-d', '--description', help='Value for the description field.', dest='desc')
    parser.add_argument('-a', '--attachment', help='Path of file to add as attachment.', type=attachment_arg,
                        dest='attach')
    parser.add_argument('-l', '--labels', nargs='*', help='Jira labels to add to new issues.', dest='labels',
                        default=JIRA_LABELS,
                        type=str)
    parser.add_argument('-j', '--jira-closed-status', nargs='*', help='Jira statuses that are considered to be closed.',
                        dest='jira_closed',
                        default=JIRA_CLOSED,
                        type=str)
    parser.add_argument('-t', '--jira-type', help='Jira issue type for new tasks.', dest='type', default=JIRA_TYPE,
                        required=False)
    parser.add_argument('-se', '--skip-existing', help='Do nothing if Jira already exists and open.',
                        action='store_true',
                        dest='skip_existing')
    parser.add_argument('-q', '--quiet', help='Do not print the banner.', action='store_true', dest='quiet')
    args = parser.parse_args()

    main(args.identifier,
         args.project,
         args.summary,
         desc=args.desc,
         attach=args.attach,
         labels=args.labels,
         jira_closed=args.jira_closed,
         skip_existing=args.skip_existing,
         quiet=args.quiet
         )


if __name__ == "__main__":
    interactive()
