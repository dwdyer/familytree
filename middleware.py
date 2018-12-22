from django.conf import settings
from django.db import connection
from django.http import HttpResponseRedirect
from logging import getLogger

logger = getLogger(__name__)

class QueryCountMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response


    '''This middleware will log the number of queries run and the total time
    taken for each request (with a status code of 200).'''
    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 200:
            total_time = 0
            for query in connection.queries:
                query_time = query.get('time')
                if query_time is None:
                    # The query time is stored under the key "duration" rather
                    # than "time" and is in milliseconds, not seconds.
                    query_time = query.get('duration', 0) / 1000
                total_time += float(query_time)

            logger.debug('%s queries run, total %s seconds' % (len(connection.queries), total_time))
        return response
