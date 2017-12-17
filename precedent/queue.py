from redis import Redis

from django.conf import settings


def to_str(s):
    if s is not None:
        return s.decode('ascii')


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

    def queue_item(self, item):
        self._r.lpush(self.pending_list, item)

    def get_next_item(self):
        return to_str(self._r.rpoplpush(self.pending_list, self.processing_list))

    def item_complete(self, item):
        self._r.lrem(self.processing_list, item, 0)

    def check_for_timeouts(self):
        for i in range(self._r.llen(self._to_delete_list)):
            item = self._r.rpop(self._to_delete_list)
            num_removed = self._r.lrem(self.processing_list, to_str(item), -1)

            # Requeue the item if it is still found in the processing queue
            if num_removed:
                self.queue_item(item)

        # Clone the processing list
        if self._r.llen(self.processing_list):
            self._r.restore(self._to_delete_list, 0, self._r.dump(self.processing_list))
        else:
            self._r.delete(self._to_delete_list)



queue = ProcessingQueue()