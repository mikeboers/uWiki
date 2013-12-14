import sqlalchemy as sa
import sqlalchemy.ext.mutable

from ..core import db


class RoleSetType(sa.types.TypeDecorator):

    impl = sa.String

    def process_bind_param(self, value, dialect):
        value = '|'.join(str(x).strip() for x in sorted(value or ()))
        return '|%s|' % value if value else None

    def process_result_value(self, value, dialect):
        value = (x.strip() for x in (value or '').split('|'))
        value = set(x for x in value if x)
        return value


class MutableSet(sa.ext.mutable.Mutable, set):

    @classmethod
    def coerce(cls, name, value):
        return MutableSet(value or ())

    def _make_func(name):
        original = getattr(set, name)
        def _func(self, *args, **kwargs):
            try:
                return original(self, *args, **kwargs)
            finally:
                self.changed()
        return _func

    add = _make_func('add')
    clear = _make_func('clear')
    difference_update = _make_func('difference_update')
    discard = _make_func('discard')
    intersection_update = _make_func('intersection_update')
    pop = _make_func('pop')
    remove = _make_func('remove')
    symmetric_difference_update = _make_func('symmetric_difference_update')
    update = _make_func('update')

    del _make_func


class RoleSetColumn(db.Column):

    def __init__(self, *args, **kwargs):
        args += (MutableSet.as_mutable(RoleSetType), )
        super(RoleSetColumn, self).__init__(*args, **kwargs)

