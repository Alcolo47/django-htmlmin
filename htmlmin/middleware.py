# Copyright 2013 django-htmlmin authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import re

from django.conf import settings
from htmlmin.minify import html_minify


class MarkRequestMiddleware(object):

    def __init__(self, get_response = None):
        self.get_response = get_response
	
	
    def __call__(self, request):
        self.process_request(request)
	
        response = self.get_response(request)
		
        return response

    def process_request(self, request):
        request._hit_htmlmin = True


class HtmlMinifyMiddleware(object):

    def __init__(self, get_response = None):
        self.get_response = get_response
		
		
    def __call__(self, request):
        response = self.get_response(request)
		
        self.process_response(request, response)
		
        return response

    def can_minify_response(self, request, response):
        if not getattr(request, '_hit_htmlmin', False):
            return False

        if hasattr(settings, 'EXCLUDE_FROM_MINIFYING'):
            for url_pattern in settings.EXCLUDE_FROM_MINIFYING:
                regex = re.compile(url_pattern)
                if regex.match(request.path.lstrip('/')):
                    return False

        if not 'text/html' in response['Content-Type']:
            return False
        return getattr(response, 'minify_response', True)


    def process_response(self, request, response):
        minify = getattr(settings, "HTML_MINIFY", not settings.DEBUG)
        if minify and self.can_minify_response(request, response):
            keep_comments = getattr(settings, 'KEEP_COMMENTS_ON_MINIFYING', False)
            parser = getattr(settings, 'HTML_MIN_PARSER', 'html5lib')
            response.content = html_minify(response.content,
                                           ignore_comments=not keep_comments,
                                           parser=parser)
            response.minify_response = False
        return response
