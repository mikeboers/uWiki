import sqlalchemy as sa


def upgrade(engine):

    meta = sa.MetaData(bind=engine)
    meta.reflect()

    col = sa.Column('is_public', sa.Boolean, nullable=False, server_default='0')
    col.create(meta.tables['pages'])
