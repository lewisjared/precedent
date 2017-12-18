from unittest import TestCase, mock

from precedent.queues import ProcessingQueue, py_to_redis, redis_to_py


class TestPyToRedis(TestCase):
    def test_str(self):
        self.assertEqual(py_to_redis('normal_string'), 'normal_string')

    def test_dict(self):
        self.assertEqual(py_to_redis({'test': 'item'}), '{"test": "item"}')


class TestRedisToPy(TestCase):
    def test_str(self):
        self.assertEqual(redis_to_py(b'normal_string'), 'normal_string')

    def test_dict(self):
        self.assertEqual(redis_to_py(b'{"test": "item"}'), {'test': 'item'})


class TestProcessingQueue(TestCase):
    def setUp(self):
        self.queue = ProcessingQueue('test_queue')
        self.r = self.queue._r

    def tearDown(self):
        self.queue.clean_up()

    def test_add_item(self):
        self.queue.queue_item('test_item')

        self.assertEqual(self.r.llen(self.queue.pending_list), 1)

        self.queue.queue_item('another_item')
        self.assertEqual(self.r.llen(self.queue.pending_list), 2)

    def test_add_item_head(self):
        self.queue.queue_item('test_item')
        self.queue.queue_item('another_item', head=True)
        self.assertEqual(self.queue.get_next_item(), 'another_item')

    def test_get_item(self):
        self.queue.queue_item('test_item')
        self.queue.queue_item('another_item')
        self.assertEqual(self.queue.get_next_item(), 'test_item')

        self.assertEqual(self.r.llen(self.queue.processing_list), 1)

    def test_empty_queue(self):
        self.assertTrue(self.queue.get_next_item() is None)

    def test_timeout(self):
        self.queue.queue_item('test_item')
        self.queue.queue_item('another_item')
        self.assertEqual(self.queue.get_next_item(), 'test_item')

        self.queue.check_for_timeouts()
        self.assertEqual(self.r.llen(self.queue._to_delete_list), 1)
        self.assertNotEquals(self.r.lindex(self.queue.pending_list, 0), 'test_item')

        self.queue.check_for_timeouts()
        self.assertEqual(self.r.llen(self.queue._to_delete_list), 0)
        self.assertEquals(self.r.lindex(self.queue.pending_list, 0), b'test_item')


    def test_multiple_items(self):
        self.queue.queue_item('test_item')
        self.queue.queue_item('test_item')
        self.queue.queue_item('test_item')
        self.assertEqual(self.queue.get_next_item(), 'test_item')
        self.assertEqual(self.queue.get_next_item(), 'test_item')
        self.assertEqual(self.queue.get_next_item(), 'test_item')

        self.assertEqual(self.r.llen(self.queue.processing_list), 3)
        self.queue.item_complete('test_item')
        self.assertEqual(self.r.llen(self.queue.processing_list), 0)

    def test_dict_item(self):
        item = {
            "item": "value"
        }

        self.queue.queue_item(item)
        self.assertEqual(item, self.queue.get_next_item())