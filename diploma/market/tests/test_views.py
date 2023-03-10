from django.test import TestCase

from market.urls import urlpatterns

PROJECT_URLS = [url.pattern.name for url in urlpatterns]


class ViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        pass


    def test_templates_exist(self):
        for url in PROJECT_URLS:
            if url:
                if 'detail' in url:
                    arg_list = [item.id for item in Item.objects.all()]
                    for arg in arg_list:
                        response = self.client.get(reverse(url, args=[arg]))
                        self.assertFalse(response.status_code == 404)
                else:
                    response = self.client.get(reverse(url))
                    self.assertFalse(response.status_code == 404)