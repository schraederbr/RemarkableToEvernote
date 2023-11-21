#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evernote_oauth_sample.settings")
    import httplib2

    _original_init = httplib2.Http.__init__

    def new_http_init(self, *args, **kwargs):
        kwargs['disable_ssl_certificate_validation'] = True
        _original_init(self, *args, **kwargs)

    httplib2.Http.__init__ = new_http_init
    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
