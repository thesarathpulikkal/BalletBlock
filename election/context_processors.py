def election_context(request):
    context_data = dict()
    context_data['election_is_occurring'] = request.election_is_occurring
    context_data['election_is_locked'] = request.election_is_locked
    return context_data