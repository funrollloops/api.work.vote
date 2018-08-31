from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from apps.mailman.templates.mailman.survey_email_html import write_html


class MailMaker(object):

    def __init__(
        self,
        jurisdiction,
        subject='PollWorker application from workelections.com',
        **kwargs
    ):
        # Make sure email is valid
        if settings.TEST_TO_EMAIL:
            self.to_email = settings.TEST_TO_EMAIL
        else:
            self.to_email = jurisdiction.email
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.subject = subject
        self.context = {
            'jurisdiction': jurisdiction,
        }

        self.context.update(kwargs)

        self.html_template = get_template('mailman/html_template.html')
        self.text_template = get_template('mailman/text_template.txt')

    def send(self):
        if self.context:
            c = Context(self.context)

        text_content = self.text_template.render(c)
        html_content = self.html_template.render(c)

        msg = EmailMultiAlternatives(self.subject, text_content,
                                     self.from_email, [self.to_email])
        msg.content_subtype = "html"
        msg.attach_alternative(html_content, "text/html")
        msg.send()

# These two classes could be combined, but for now keep separate
class MailSurvey(object):

    def __init__(
        self,
        jurisdictions,
        recipients,
        subject='WorkElections.com Survey',
        **kwargs
    ):
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.subject = subject
        self.to_email = recipients

        link_text = ""
        link_html = "\n"
        for pair in jurisdictions:
            link_html += '<p align="left"><a href={}>{}</a></p> \n'.format(settings.SURVEY_URL.format(pair[1]), pair[0]) 
            link_text += pair[0]+ ": " + settings.SURVEY_URL.format(pair[1]) + "\n"
        self.context={'SurveyLinkHTML': link_html, 'SurveyLinkText': link_text}
        self.html = write_html(link_html)
        self.text_template = get_template('mailman/survey_email_text.txt')

    def send(self):
        if self.context:
            c = Context(self.context)
        
        text_content = self.text_template.render(c)
        html_content = self.html

        msg = EmailMultiAlternatives(self.subject, text_content,
                                     'alyssa@developmentseed.org', [self.to_email])
        msg.content_subtype = "html"
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
            return 'OK'
        except:
            return 'ERROR'
