import sqlalchemy as sa


def upgrade(engine):

    meta = sa.MetaData(bind=engine)
    meta.reflect()

    new_table = sa.Table('new_table', meta,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
    )
    new_table.create()

    new_col = sa.Column('new_col', sa.String, nullable=False, server_default='')
    new_col.create(meta.tables['existing'])

