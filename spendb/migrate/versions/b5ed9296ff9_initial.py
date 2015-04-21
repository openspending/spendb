"""initial

Revision ID: b5ed9296ff9
Revises: None
Create Date: 2015-04-21 08:55:07.628161

"""

# revision identifiers, used by Alembic.
revision = 'b5ed9296ff9'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('account',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=255), nullable=True),
        sa.Column('fullname', sa.Unicode(length=2000), nullable=True),
        sa.Column('email', sa.Unicode(length=2000), nullable=True),
        sa.Column('public_email', sa.Boolean(), nullable=True),
        sa.Column('twitter_handle', sa.Unicode(length=140), nullable=True),
        sa.Column('public_twitter', sa.Boolean(), nullable=True),
        sa.Column('password', sa.Unicode(length=2000), nullable=True),
        sa.Column('api_key', sa.Unicode(length=2000), nullable=True),
        sa.Column('admin', sa.Boolean(), nullable=True),
        sa.Column('script_root', sa.Unicode(length=2000), nullable=True),
        sa.Column('terms', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('dataset',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=255), nullable=True),
        sa.Column('label', sa.Unicode(length=2000), nullable=True),
        sa.Column('description', sa.Unicode(), nullable=True),
        sa.Column('currency', sa.Unicode(), nullable=True),
        sa.Column('default_time', sa.Unicode(), nullable=True),
        sa.Column('schema_version', sa.Unicode(), nullable=True),
        sa.Column('category', sa.Unicode(), nullable=True),
        sa.Column('private', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('data', sa.Unicode(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('dataset_territory',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.Unicode(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('dataset_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['dataset_id'], ['dataset.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dataset_language',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.Unicode(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('dataset_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['dataset_id'], ['dataset.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('run',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('operation', sa.Unicode(), nullable=True),
        sa.Column('status', sa.Unicode(), nullable=True),
        sa.Column('source', sa.Unicode(), nullable=True),
        sa.Column('time_start', sa.DateTime(), nullable=True),
        sa.Column('time_end', sa.DateTime(), nullable=True),
        sa.Column('dataset_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['dataset_id'], ['dataset.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('account_dataset',
        sa.Column('dataset_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
        sa.ForeignKeyConstraint(['dataset_id'], ['dataset.id'], ),
        sa.PrimaryKeyConstraint('dataset_id', 'account_id')
    )
