import sqlalchemy as sa


def upgrade(engine):

    meta = sa.MetaData(bind=engine)
    meta.reflect()


    pages = sa.Table('pages', meta,

        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, unique=True, nullable=False),

        # One of these should be set.
        sa.Column('title', sa.String),
        sa.Column('redirect', sa.String),

    )
    pages.create()


    contents = sa.Table('page_contents', meta,

        sa.Column('id', sa.Integer, primary_key=True),

        sa.Column('page_id', sa.Integer, sa.ForeignKey('pages.id'), nullable=False),

        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),

        sa.Column('content', sa.String, nullable=False),

    )
    contents.create()
