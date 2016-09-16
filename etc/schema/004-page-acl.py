import sqlalchemy as sa


def upgrade(engine):

    meta = sa.MetaData(bind=engine)
    meta.reflect()

    col = sa.Column('acl', sa.String, nullable=False, server_default='ALL+rw')
    col.create(meta.tables['pages'])
