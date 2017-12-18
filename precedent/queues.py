import json

from django.conf import settings
from redis import Redis


def redis_to_py(s):
    if s is not None:
        try:
            s = s.decode('ascii')
            return json.loads(s)
        except ValueError:
            return s


def py_to_redis(s):
    if isinstance(s, str):
        return s
    try:
        return json.dumps(s)
    except ValueError:
        return s


class ProcessingQueue(object):
    """
    Implements a reliable queue

    Uses RPOPLPUSH redis command to enable the tracking of processing tasks. See https://redis.io/commands/rpoplpush for more information
    """

    def __init__(self, queue_name='github'):
        self._r = Redis.from_url(settings.REDIS_URL)
        self.pending_list = 'queue_' + queue_name
        self.processing_list = self.pending_list + '_processing'
        self._to_delete_list = self.pending_list + '_to_delete'

    def clean_up(self):
        self._r.delete(self.pending_list, self.processing_list, self._to_delete_list)

    def queue_item(self, item, head=False):
        """
        Queue up an item to be processed at a later date

        :param item: The item to be queued. Can be either a dict, list or string
        :param head: If True, put the item at the head of the queue to be processed next, else FILO
        """
        if head:
            self._r.rpush(self.pending_list, py_to_redis(item))
        else:
            self._r.lpush(self.pending_list, py_to_redis(item))

    def get_next_item(self):
        return redis_to_py(self._r.rpoplpush(self.pending_list, self.processing_list))

    def item_complete(self, item):
        self._r.lrem(self.processing_list, item, 0)

    def check_for_timeouts(self):
        for i in range(self._r.llen(self._to_delete_list)):
            item = self._r.rpop(self._to_delete_list)
            item = redis_to_py(item)
            num_removed = self._r.lrem(self.processing_list, item, -1)

            # Requeue the item if it is still found in the processing queue
            if num_removed:
                self.queue_item(item)

        # Clone the processing list
        if self._r.llen(self.processing_list):
            self._r.restore(self._to_delete_list, 0, self._r.dump(self.processing_list))
        else:
            self._r.delete(self._to_delete_list)


queue = ProcessingQueue()
