from django.conf import settings
from djangotoolbox.utils import make_tls_property
from django.contrib.sites.models import Site
from dbtemplates.models import Template
from cms.models import Page


CMS_TEMPLATES = settings.__class__.CMS_TEMPLATES = make_tls_property()

class DBTemplatesMiddleware(object):
    def process_request(self, request):
        site_id = request.session.get('cms_admin_site', None)
        available_sites = []
        if site_id:
            available_sites.append(Site.objects.get(pk=site_id))
        try:
            s = Site.objects.get(name='PBS')
        except Site.DoesNotExist:
            pass
        else:
            available_sites.append(s)
        t = Template.objects.filter(sites__in=available_sites).distinct()
        CMS_TEMPLATES.value = [(templ.name, templ.name) for templ in t]
        if not CMS_TEMPLATES.value:
            CMS_TEMPLATES.value = [('dummy', 'Please create a template first.')]

        # This is a huge hack.
        # Expand the model choices field to contain all templates.
        all_templates = Template.objects.all().values_list('name')
        choices = [t*2 for t in all_templates]
        if settings.CMS_TEMPLATE_INHERITANCE:
            choices += [('INHERIT', 'INHERIT')]
        Page._meta.get_field_by_name('template')[0].choices[:] = choices
