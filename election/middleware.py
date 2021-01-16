from election.business import ElectionBusiness

class ElectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        eb = ElectionBusiness()
        election_is_occurring = eb.isOccurring()
        election_is_locked = eb.isLocked()
        request.election_is_occurring = election_is_occurring
        request.election_is_locked = election_is_locked
        
        response = self.get_response(request)

        response.election_is_occurring = election_is_occurring
        response.election_is_locked = election_is_locked
        # Code to be executed for each request/response after
        # the view is called.

        return response
