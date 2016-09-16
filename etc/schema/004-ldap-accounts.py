import sqlalchemy as sa


def upgrade(engine):

    meta = sa.MetaData(bind=engine)
    meta.reflect()

    col = sa.Column('groups', sa.String)
    col.create(meta.tables['users'])
