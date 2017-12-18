from unittest import TestCase, mock

from precedent.models import Owner, Repo
from precedent.spiders import GithubSpider, QueryException
from github import RateLimitExceededException, ContentFile

from github.Repository import Repository
from github.NamedUser import NamedUser

class MockGithub(object):
    total_count = 1

    def __init__(self):
        self.search_code_result = mock.Mock(return_value=[mock.Mock()])
        self.search_code = mock.Mock(return_value=self.search_code_result)


class TestGithubSpider(TestCase):
    def setUp(self):
        self.s = GithubSpider()

    def test_iter(self):
        s = GithubSpider()
        terms = [t for t in s]
        # There should be lots
        self.assertGreater(len(terms), 10)

    def test_type(self):
        s = GithubSpider()
        terms = [t for t in s]
        t = terms[0]
        self.assertTrue(isinstance(t, dict))
        self.assertEqual(t['type'], 'n')
        self.assertEqual(t['page'], 1)
        self.assertIn(self.s.SEARCH_TERMS['n'], t['term'])

    @mock.patch('precedent.spiders.Github.search_code')
    def test_process(self, mock_gh):
        mock_gh().get_page.return_value = []
        mock_gh().totalCount = 1
        s = GithubSpider()
        term = 'filename:package.json+-path=node_modules+size=37'
        s.process_query({
            'type': 'n',
            'term': term,
            'page': 1
        })
        mock_gh.assert_called_with(term)
        mock_gh().get_page.assert_called_with(1)

    @mock.patch('precedent.spiders.Github.search_code')
    def test_process_valid(self, mock_gh):
        mock_res = mock.MagicMock()
        mock_gh().get_page.return_value = [mock_res]
        mock_gh().totalCount = 1
        s = GithubSpider()
        s._serialize_repo = mock.MagicMock()
        term = 'filename:package.json+-path=node_modules+size=37'
        s.process_query({
            'type': 'n',
            'term': term,
            'page': 1
        })
        s._serialize_repo.assert_called_with(mock_res)

    @mock.patch('precedent.spiders.Github.search_code')
    def test_process_too_many(self, mock_gh):
        mock_gh().get_page.return_value = []
        mock_gh().totalCount = 10000
        s = GithubSpider()
        self.assertRaises(QueryException, s.process_query, {
            'type': 'n',
            'term': 'filename:package.json+-path=node_modules+size=37',
            'page': 10
        })

    @mock.patch('precedent.spiders.Github.search_code')
    def test_process_new_page(self, mock_gh):
        mock_gh().get_page.return_value = []
        mock_gh().totalCount = 10000
        s = GithubSpider()
        res = s.process_query({
            'type': 'n',
            'term': 'filename:package.json+-path=node_modules+size=37',
            'page': 1
        })

        self.assertEqual(res['page'], 2)
        self.assertEqual(res['term'], 'filename:package.json+-path=node_modules+size=37')

    @mock.patch('precedent.spiders.Github.search_code')
    def test_rate_limit(self, mock_gh):
        mock_gh.side_effect = RateLimitExceededException(400, '')
        s = GithubSpider()
        self.assertRaises(QueryException, s.process_query, {
            'type': 'n',
            'term': 'filename:package.json+-path=node_modules+size=37',
            'page': 10
        })

    @mock.patch('precedent.spiders.Github.search_code')
    def test_exc(self, mock_gh):
        mock_gh.side_effect = RateLimitExceededException(400, '')
        s = GithubSpider()
        try:
            s.process_query({
                'type': 'n',
                'term': 'filename:package.json+-path=node_modules+size=37',
                'page': 10
            })
        except QueryException as e:
            self.assertIn('rate limit', str(e))

    def _create_example_resp(self):
        m_owner = mock.Mock(spec=NamedUser, id=1)
        m_owner.name = 'test'
        m_owner.type = 'Organization'
        m_owner.url = 'a'
        m_owner.avatar_url = 'a'

        m_repo = mock.Mock(spec=Repository, id=2, owner=m_owner)
        m_repo.name = 'repo'
        m_repo.full_name = 'test/repo'
        m_repo.url = 'a'
        m_repo.description = 'adgfzdf'
        return mock.MagicMock(spec=ContentFile.ContentFile, repository=m_repo)

    def test_serialize(self):
        r = self._create_example_resp()
        s = GithubSpider()

        s._serialize_repo(r)
        Owner.objects.get(name=r.repository.owner.name)

        # Check that it is imdepontent
        s._serialize_repo(r)
        self.assertEqual(Owner.objects.count(), 1)
        self.assertEqual(Repo.objects.count(), 1)
