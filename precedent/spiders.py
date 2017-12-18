from logging import getLogger

from django.conf import settings
from github import Github, RateLimitExceededException

from precedent.models import Package, Repo

logger = getLogger(__name__)


class QueryException(Exception):
    def __init__(self, query, *args):
        super(QueryException, self).__init__(*args)
        self.query = query


class Spider(object):
    SEARCH_TERMS = {

    }

    def __iter__(self):
        for k, term in self.SEARCH_TERMS.items():
            for t in self.get_terms(k, term):
                yield t

    def get_terms(self, key, term):
        return {
            'type': key,
            'term': term,
            'page': 1,
        }

    def process_query(self, query):
        """
        Perform the API lookup

        This should be implemented by the overriding class
        :return:
        """
        raise NotImplemented


class GithubSpider(Spider):
    SEARCH_TERMS = {
        Package.Source.npm: 'filename:package.json+-path=node_modules'
    }
    per_page = 100

    def __init__(self):
        self._g = Github(settings.GITHUB_ACCESS_TOKEN, per_page=self.per_page)

    def _serialize_repo(self, item):
        return Repo.objects.create(

        )

    def get_terms(self, key, term):
        for size in range(10000):
            term_size = term + '+size={}'.format(size)
            yield super(GithubSpider, self).get_terms(key, term_size)

    def process_query(self, query):
        try:
            search = self._g.search_code(query['term'])
            items = search.get_page(query['page'])
            for item in items:
                repo = self._serialize_repo(item)
                repo.save()

            if search.totalCount > query['page'] * self.per_page:
                if query['page'] == 10:
                    # We have ran out of search queries
                    raise QueryException(query, 'too many results')

                new_query = {
                    'type': query['type'],
                    'term': query['term'],
                    'page': query['page'] + 1,
                }
                return new_query

        except RateLimitExceededException:
            logger.warning('Rate limit exceeded. Requeue and try again')
            raise QueryException(query, 'rate limit exceeded. Requeue and try again')

