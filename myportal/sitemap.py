import datetime
import time

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from globus_portal_framework.apps import get_setting
from globus_portal_framework.gsearch import get_search_query, get_search_filters, post_search


class GeoFileSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.6

    def items(self):
        query = get_setting('DEFAULT_QUERY')
        # filters = get_search_filters()
        search_result = post_search('schema-org-index', query, [], None,
                                    1)  # todo replace index with variable
        # print(f'[GeoFileSitemap | items] search_result={search_result}')

        id_list = []
        for subject_data in search_result['search_results']:
            print(f'[GeoFileSitemap | items] subject_data={subject_data}')

            id_list.append(subject_data['subject'])

        return id_list

    def lastmod(self, obj):
        return datetime.datetime.now()

    def location(self, obj):
        # reverse(obj)
        return reverse('resource', kwargs={'index': 'schema-org-index', 'uuid': obj})
