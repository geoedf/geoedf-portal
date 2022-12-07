import datetime
import time

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from globus_portal_framework.apps import get_setting
from globus_portal_framework.gsearch import get_search_query, get_search_filters, post_search


def get_geofile_id_list():  # 返回对象的列表.这些对象将被其他方法或属性调用
    query = get_setting('DEFAULT_QUERY')
    # filters = get_search_filters()
    search_result = post_search('schema-org-index', query, None, None,
                                1)  # todo replace index with variable
    print(f'[GeoFileSitemap | items]{search_result}')
    id_list = ['www.google.com', 'www.reddit.com']
    return id_list
    # return search_result

class GeoFileSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.6

    def items(self):  # 返回对象的列表.这些对象将被其他方法或属性调用
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

    def lastmod(self, obj):  # 可选,该方法返回一个datetime,表示每个对象的最后修改时间
        return datetime.datetime.now()

    def location(self, obj):  # 可选.返回每个对象的绝对路径.如果对象有get_absolute_url()方法,可以省略location
        # reverse(obj)
        return reverse('resource', kwargs={'index': 'schema-org-index', 'uuid':obj})