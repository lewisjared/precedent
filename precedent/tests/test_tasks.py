from unittest import TestCase
from unittest.mock import patch

from precedent.tasks import check_queues, process_queue


class TestCheckQueues(TestCase):
    @patch('precedent.tasks.queue')
    def test_calls_check_timeout(self, mock_queue):
        check_queues()
        self.assertEqual(mock_queue.check_for_timeouts.call_count, 1)


class TestProcessQueue(TestCase):
    @patch('precedent.tasks.queue')
    def test_calls_check_timeout(self, mock_queue):
        mock_queue.get_next_item.return_value = None
        res = process_queue()
        self.assertIsNone(res)

    @patch('precedent.tasks.queue')
    @patch('precedent.tasks.GithubSpider')
    def test_checks_query(self, mock_spider, mock_queue):
        spider_inst = mock_spider.return_value
        process_queue()
        spider_inst.process_query.assert_called_with(mock_queue.get_next_item.return_value)

        # The next query is requeued at the front of the queue
        mock_queue.queue_item.assert_called_with(spider_inst.process_query.return_value, head=True)

    @patch('precedent.tasks.queue')
    @patch('precedent.tasks.GithubSpider')
    def test_completed_query_not_requeued(self, mock_spider, mock_queue):
        spider_inst = mock_spider.return_value
        spider_inst.process_query.return_value = None
        process_queue()
        mock_queue.queue_item.assert_not_called()

    @patch('precedent.tasks.queue')
    @patch('precedent.tasks.GithubSpider')
    def test_(self, mock_spider, mock_queue):
        spider_inst = mock_spider.return_value
        spider_inst.process_query.return_value = None
        process_queue()
        mock_queue.queue_item.assert_not_called()