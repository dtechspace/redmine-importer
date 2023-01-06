"""Markdown CustomConverter class, which uses the python library markdownify 
and customizes certain markdown styles to match Redmine markdown formatting.

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

from markdownify import MarkdownConverter, chomp, abstract_inline_conversion
from assembla_download import download_file_attachment
import imghdr
import cairosvg
import os

uploads = []

class CustomConverter(MarkdownConverter):
    """
    Create a custom MarkdownConverter to handle Redmine's markdown format
    """ 
    def convert_hn(self, n, el, text, convert_as_inline):
        """
        Converts HTML headers to Redmine markdown headers.
        """
        if convert_as_inline:
            return text

        style = self.options['heading_style'].lower()
        text = text.rstrip()
        hashes = '\nh{}.'.format(n)
        
        return '%s %s\n\n' % (hashes, text)
    
    def convert_img(self, el, text, convert_as_inline):
        """
        Downloads image from Assembla and imports/formats the image for Redmine.
        """
        alt = el.attrs.get('alt', None) or ''
        src = el.attrs.get('src', None) or ''
        title = el.attrs.get('title', None) or ''
        style = '' if not el.attrs.get('style', None) else '{'+el.attrs.get('style', '')+'}'
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
        if "assembla" in src:
            url_split = src.split('/')
            space_id, doc_id = url_split[4], url_split[6]
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
                uploads.append({'path' : img_abs_path, 'filename' : img_name})
                return '\n!%s%s!\n' % (style, img_name)
        elif "spaces" in src:
            url_split = src.split('/')
            space_id, doc_id = url_split[2], url_split[4]
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
                uploads.append({'path' : img_abs_path, 'filename' : img_name})
                return '\n!%s%s!\n' % (style, img_name)
        return '\n!%s%s!\n' % (style, src)
    
    def convert_pre(self, el, text, convert_as_inline):
        """ 
        Converts code blocks from Assembla to Redmine markdown.
        """
        if not text:
            return ''
        code_language = self.options['code_language']

        if self.options['code_language_callback']:
            code_language = self.options['code_language_callback'](el) or code_language

        return '<pre>%s%s</pre>' % (code_language, text)

    
    def convert_a(self, el, text, convert_as_inline):
        """ 
        Converts links from Assembla to Redmine markdown.
        """
        prefix, suffix, text = chomp(text)
        if not text:
            return ''
        href = el.get('href')
        title = el.get('title')
        # For the replacement see #29: text nodes underscores are escaped
        if not href or '/wiki/' in href: 
            return text
        if (self.options['autolinks']
                and text.replace(r'\_', '_') == href
                and not title
                and not self.options['default_title']):
            # Shortcut syntax
            return '<%s>' % href
        if self.options['default_title'] and not title:
            title = href
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
        return '[%s](%s)' % (text, href) if href else text

    def convert_code(self, el, text, convert_as_inline):
        """ 
        Converts inline code from Assembla to Redmine markdown.
        """
        if el.parent.name == 'pre':
            return text
        elif '\n' in text: 
            return self.convert_pre(el, text, convert_as_inline)
        else:
            converter = abstract_inline_conversion(lambda self: '@')
            return converter(self, el, text, convert_as_inline)
    

    def convert_li(self, el, text, convert_as_inline):
        """ 
        Converts lists from Assembla to Redmine markdown.
        """
        parent = el.parent
        if parent is not None and parent.name == 'ol':
            if parent.get("start"):
                start = int(parent.get("start"))
            else:
                start = 1
            bullet = '%s.' % (start + parent.index(el))
        else:
            depth = 0
            while el:
                if el.name == 'ul':
                    depth += 1
                el = el.parent
            bullet = "*"*depth
        return '%s %s\n' % (bullet, (text or '').strip())


    convert_del = abstract_inline_conversion(lambda self: '-')
    convert_s = convert_del

def md(html, temp_list, **options):
    """
    Entrypoint function for markdown conversion between Assembla HTML and 
    Redmine using the CustomConverter class.
    """

    global uploads
    uploads = temp_list
    return CustomConverter(**options).convert(html), uploads