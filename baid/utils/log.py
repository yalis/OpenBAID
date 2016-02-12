import logging
from django.conf import settings
from django.core import mail
from django.core.mail import get_connection
from django.utils.encoding import force_text
from django.views.debug import ExceptionReporter, get_exception_reporter_filter


class AdminEmailMandrilHandler(logging.Handler):
    """
    Custom admin email mandril handler
    """
    def __init__(self, include_html=True, email_backend='baid.utils.mail.backends.mandrill.DjangoMandrillBackend'):
        logging.Handler.__init__(self)
        self.include_html = include_html
        self.email_backend = email_backend

    def emit(self, record):
        try:
            request = record.request
            subject = '%s (%s IP): %s' % (
                record.levelname,
                ('internal' if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS
                 else 'EXTERNAL'),
                record.getMessage()
            )
            filter = get_exception_reporter_filter(request)
            request_repr = '\n{0}'.format(force_text(filter.get_request_repr(request)))
        except Exception:
            subject = '%s: %s' % (
                record.levelname,
                record.getMessage()
            )
            request = None
            request_repr = "unavailable"
        subject = self.format_subject(subject)

        if record.exc_info:
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)

        message = "%s\n\nRequest repr(): %s" % (self.format(record), request_repr)
        reporter = ExceptionReporter(request, is_email=True, *exc_info)
        html_message = reporter.get_traceback_html() if self.include_html else None
        mail.mail_admins(subject, message, fail_silently=True,
                         html_message=html_message,
                         connection=self.connection())

    def connection(self):
        return get_connection(backend=self.email_backend, fail_silently=True)

    def format_subject(self, subject):
        formatted_subject = subject.replace('\n', '\\n').replace('\r', '\\r')
        return formatted_subject[:989]