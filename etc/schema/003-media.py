import sqlalchemy as sa


def upgrade(engine):

    meta = sa.MetaData(bind=engine)
    meta.reflect()

    objects = sa.Table('media_objects', meta,

        sa.Column('id', sa.Integer, primary_key=True),

        sa.Column('type', sa.String, nullable=False),
        sa.Column('slug', sa.String, nullable=False),
        sa.UniqueConstraint('type', 'slug'),

        sa.Column('title', sa.String),
        sa.Column('latest_id', sa.Integer, sa.ForeignKey('media_versions.id')),

    )

    redirects = sa.Table('media_redirects', meta,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('type', sa.String, nullable=False),
        sa.Column('slug', sa.String, nullable=False),
        sa.UniqueConstraint('type', 'slug'),
        sa.Column('dest', sa.String, nullable=False),
    )

    versions = sa.Table('media_versions', meta,

        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('object_id', sa.Integer, sa.ForeignKey('media_objects.id'), nullable=False),

        sa.Column('acl', sa.String),

        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('created_by_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),

        sa.Column('content', sa.String, nullable=False),

    )

    objects.create()
    redirects.create()
    versions.create()
