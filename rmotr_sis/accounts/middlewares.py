from datetime import datetime


class LastActivityMiddleware(object):

    def process_request(self, request):

        # NOTE: This could cause performance issues in the future, but considering
        # the current traffic rates we have right now it shouldn't be a problem.
        if request.user.is_authenticated():
            request.user.last_activity = datetime.now()
            request.user.save()
