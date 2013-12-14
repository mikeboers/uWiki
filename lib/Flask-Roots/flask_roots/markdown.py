"""

Original taken from:
    http://gregbrown.co.nz/code/githib-flavoured-markdown-python-implementation/

I (mikeboers) have adapted it to work properly. It was only replacing newlines
at the very start of of a blob of text. I also removed the emphasis fixer
cause my markdown does it anyways, and this was screwing up flickr links.

The hash should really be salted.

Github flavoured markdown - ported from
http://github.github.com/github-flavored-markdown/

Usage:

    html_text = markdown(gfm(markdown_text))

(ie, this filter should be run on the markdown-formatted string BEFORE the markdown
filter itself.)

"""


from __future__ import absolute_import

import os
import logging
import re
import cgi

from flask import current_app
import markdown as _markdown
from markdown.extensions.codehilite import CodeHiliteExtension

log = logging.getLogger(__name__)


class MathJaxExtension(_markdown.Extension):
    
    class Preprocessor(_markdown.preprocessors.Preprocessor):
         
        _pattern = re.compile(r'\\\[(.+?)\\\]|\\\((.+?)\\\)', re.MULTILINE | re.DOTALL)

        def _callback(self, m):
            return self.markdown.htmlStash.store(cgi.escape(m.group(0)), safe=True)
        
        def run(self, lines):
            """Parses the actual page"""
            return self._pattern.sub(self._callback, '\n'.join(lines)).splitlines() + ['']
        
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('mathjax', self.Preprocessor(md), '<html_block')


class MarkdownEscapeExtension(_markdown.Extension):
    
    class Preprocessor(_markdown.preprocessors.Preprocessor):
         
        _pattern = re.compile(r'<nomarkdown>(.+?)</nomarkdown>', re.MULTILINE | re.DOTALL)

        def _callback(self, m):
            return self.markdown.htmlStash.store(m.group(1), safe=True)
        
        def run(self, lines):
            """Parses the actual page"""
            return self._pattern.sub(self._callback, '\n'.join(lines)).splitlines() + ['']
        
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('markdown_escape', self.Preprocessor(md), '<html_block')
        

extension_constructors = dict(
    mathjax=MathJaxExtension,
    markdown_escape=MarkdownEscapeExtension,
    codehilite=lambda: CodeHiliteExtension([('guess_lang', False)])
)


extension_usage_defaults = dict(
    nl2br=True,
    codehilite=True,
    mathjax=True,
    markdown_escape=False,
    abbr=True,
    footnotes=True,
    fenced_code=True,
)


def markdown(text, _unknown=None, **custom_exts):
    # _unknown is for swisssol.com. It may have been nl2br.

    if not isinstance(text, unicode):
        text = unicode(str(text), 'utf8')
    
    loaded_extensions = []
    ext_prefs = extension_usage_defaults.copy()
    ext_prefs.update(current_app.config.get('MARKDOWN_EXTS', {}))
    ext_prefs.update(custom_exts)
    for name, include in ext_prefs.iteritems():
        if include:
            ext = extension_constructors.get(name)
            ext = ext() if ext else name
            loaded_extensions.append(ext)
        
    md = _markdown.Markdown(extensions=loaded_extensions,
                  safe_mode=False, 
                  output_format='xhtml')
    return md.convert(text)
    

