import sqlalchemy as sa


def upgrade(engine):

    meta = sa.MetaData(bind=engine)
    meta.reflect()

    table = meta.tables['pages']
    sa.Column('owner_id', sa.Integer, sa.ForeignKey('users.id')).create(table)
    sa.Column('group', sa.String).create(table)
    sa.Column('group_perms', sa.String, server_default='write').create(table)
    sa.Column('other_perms', sa.String, server_default='write').create(table)
    sa.Column('anon_perms', sa.String, server_default='read').create(table)
    sa.Column('custom_acl', sa.String).create(table)
