from django.conf import settings
from django.db import connection
from django.http import HttpResponseRedirect
from logging import getLogger

logger = getLogger(__name__)

class QueryCountMiddleware:
    '''This middleware will log the number of queries run and the total time
    taken for each request (with a status code of 200).'''
    def process_response(self, request, response):
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


class LoginRequiredMiddleware:
    '''Require the user to be logged in to access any page other than the login
    page. This is better than having to annotate each view method separately.'''
    def process_response(self, request, response):
        path = request.path_info.strip('/')
        if path != settings.LOGIN_URL.strip('/'):
            if hasattr(request, 'user') and not request.user.is_authenticated():
                return HttpResponseRedirect(settings.LOGIN_URL)
        return response
