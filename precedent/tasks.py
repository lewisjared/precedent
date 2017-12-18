from logging import getLogger

from celery import shared_task

from precedent.queues import queue
from precedent.spiders import GithubSpider, QueryException

logger = getLogger(__name__)


@shared_task
def find_repos():
    """
    Finds all repos matching the search criteria for a number of different package manager.

    Note that this queues up 1000s of search queries which can take days to work through. This query should only be run periodically to capture newly
    created projects.
    :return:
    """
    logger.info('beginning to queue new search terms')
    count = 0
    spider = GithubSpider()
    for search_query in spider:
        logger.info('queuing search query: {}'.format(search_query))
        queue.queue_item(search_query)
        count += 1

    logger.info('added {} search queries'.format(count))


@shared_task
def check_queues():
    """
    Checks for any tasks that have not successfully completed and requeues them

    This task should be run periodically. Currently being run every 1m
    :return:
    """
    queue.check_for_timeouts()


@shared_task
def process_queue():
    query = queue.get_next_item()

    if query is None:
        return

    logger.info("processing query: {}".format(query))

    # if any exceptions are raised then the item will be reprocessed at a later date
    spider = GithubSpider()
    try:
        next_query = spider.process_query(query)

        if next_query is not None:
            queue.queue_item(next_query, head=True)

        # mark the item as complete, removing it from the processing queue
        queue.item_complete(query)
    except QueryException as e:
        logger.warning('Exception in processing {}: {}'.format(e.query, e))


@shared_task
def process_package_file(repo, url):
    """
    Processes a new incoming package file

    This could be for an new repo or an update to an old one
    :param repo:
    :param url:
    :return:
    """
    pass