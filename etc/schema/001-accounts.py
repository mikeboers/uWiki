import sqlalchemy as sa


def upgrade(engine):

    meta = sa.MetaData(bind=engine)
    meta.reflect()


    users = sa.Table('users', meta,

        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),

        sa.Column('password_hash', sa.String),
        sa.Column('roles', sa.String),

        sa.Column('display_name', sa.String, nullable=False, server_default=''),
        sa.Column('email', sa.String, nullable=False, server_default=''),

    )
    users.create()
