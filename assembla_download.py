"""
Helper functions to access and download assets from the associated
Assembla space, with credentials provided in the settings.ini file.

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

import requests, os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from assembla import API
import configparser
import re
import imghdr
import cairosvg

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

config = configparser.ConfigParser()
config.read('settings.ini')
ASSEMBLA_API_KEY = config['Assembla Keys']['ASSEMBLA_API_KEY']
ASSEMBLA_API_KEY_SECRET = config['Assembla Keys']['ASSEMBLA_API_KEY_SECRET']
ASSEMBLA_SPACE = config['Assembla Keys']['ASSEMBLA_SPACE'] 

assembla = API(key=ASSEMBLA_API_KEY, secret=ASSEMBLA_API_KEY_SECRET)
my_space = assembla.spaces(name=ASSEMBLA_SPACE)[0]
    
def download_file_attachment(space_id, document_id):
    """
    Returns the contents of the document associated with the given space_id and 
    document_id from Assembla. 
    """
    try:
        ASSEMBLA_BASE_URL = 'https://api.assembla.com/v1/'
        url = os.path.join(
            ASSEMBLA_BASE_URL, 
            "spaces", 
            space_id, 
            "documents", 
            str(document_id), 
            "download"
        )
        response = get_assembla(url)
        return response
    except:
        return None
 
def get_assembla(url, params={}, headers={}):
    """
    Makes a request to the given Assembla API using API key/secret credentials.
    """
    headers = { 'X-Api-Key': ASSEMBLA_API_KEY,
                'X-Api-Secret' : ASSEMBLA_API_KEY_SECRET,
            }
    retry_count = 0
    response = None
    while retry_count < 5:
        try:
            response = requests.get(
                url, 
                params=params, 
                headers=headers, 
                verify=False, 
                allow_redirects=True
            )
            break
        except:
            retry_count += 1
    return response


def get_assembla_pages():
    """
    Returns all wiki pages associated with the given Assembla space.
    """
    return my_space.wiki_pages(extra_params={'per_page': 10})
    
def get_assembla_tickets():
    """
    Returns all tickets associated with the given Assembla space.
    """
    return my_space.tickets(extra_params={'per_page': 10})

def assembla_to_redmine_markdown(text):
    """
    Converts from Assembla markdown to Redmine markdown; used for ticket/issue
    formatting.
    """
    uploads = []
    text = re.sub(r"###([^\n]*)###", r"###\1", text)
    text = re.sub(r"##([^\n]*)##", r"##\1", text)
    text = re.sub(r"#([^\n]*)#", r"###\1", text)
    text = re.sub(r"h1.([^\n]*)", r"h1.\1\n", text)
    text = re.sub(r"h2.([^\n]*)", r"h2.\1\n", text)
    text = re.sub(r"h3.([^\n]*)", r"h3.\1\n", text)

    text = re.sub(r"\[\[image:(.*)\|.*\]\]", r"[[image:\1|", text)
    imgs = re.findall(r"\[\[image:.*\|", text)
    for img in imgs:
        doc_id = img[8:-1]
        space_id = my_space['id']
        response = download_file_attachment(space_id, doc_id)
        if response.status_code == 200:
            img_abs_path = 'img/{}_{}'.format(space_id, doc_id)
            with open(img_abs_path, 'wb') as f:
                f.write(response.content)
            ext = imghdr.what(img_abs_path)
            # if ext is an svg file
            if not ext: 
                png_path = img_abs_path + '.png'
                cairosvg.svg2png(url=img_abs_path, write_to=png_path)
                img_abs_path = png_path
                ext = 'png'
            else:
                os.rename(img_abs_path, img_abs_path + '.' + ext)
                img_abs_path += '.' + ext
            img_name = '{}_{}.{}'.format(space_id, doc_id, ext)
            text = re.sub(fr"\[\[image:{doc_id}\|", fr"!{img_name}!", text)
            uploads.append({'path' : img_abs_path, 'filename' : img_name})
        
    return text, uploads