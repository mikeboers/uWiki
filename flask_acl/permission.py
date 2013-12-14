from collections import Container, Callable

from .globals import current_auth


# Permissions
class All(object):
    def __contains__(self, other):
        return True
    def __repr__(self):
        return 'ALL'

   
default_permission_sets = {
    'ALL': All(),
    'http.get': set(('http.get', 'http.head', 'http.options')),
}


def parse_permission_set(input):
    if isinstance(input, basestring):
        try:
            return current_auth.permission_sets[input]
        except KeyError:
            raise ValueError('unknown permission set %r' % input)
    return input


def check_permission(perm, perm_set):
    if isinstance(perm_set, basestring):
        return perm == perm_set
    elif isinstance(perm_set, Container):
        return perm in perm_set
    elif isinstance(perm_set, Callable):
        return perm_set(perm)
    else:
        raise TypeError('permission set must be a string, container, or callable')
