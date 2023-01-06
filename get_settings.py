"""Prints all Assembla spaces and Redmine projects associated with the API keys 
provided in the settings.ini file.

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

import configparser
from redminelib import Redmine
from assembla import API

config = configparser.ConfigParser()
config.read('settings.ini')
ASSEMBLA_API_KEY = config['Assembla Keys']['ASSEMBLA_API_KEY']
ASSEMBLA_API_KEY_SECRET = config['Assembla Keys']['ASSEMBLA_API_KEY_SECRET']
ASSEMBLA_SPACE = config['Assembla Keys']['ASSEMBLA_SPACE'] 

assembla = API(key=ASSEMBLA_API_KEY, secret=ASSEMBLA_API_KEY_SECRET)
print("Assembla Spaces", assembla.spaces())


REDMINE_API_KEY = config['Redmine Keys']['REDMINE_API_KEY']
REDMINE_URL = config['Redmine Keys']['REDMINE_URL']
REDMINE_PROJECT = config['Redmine Keys']['REDMINE_PROJECT']

redmine = Redmine(REDMINE_URL, key=REDMINE_API_KEY)

print("Redmine Projects: ", [p.identifier for p in redmine.project.all()])

