"""init

Revision ID: cda54b3bb494
Revises:
Create Date: 2017-07-11 14:40:02.424648

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'cda54b3bb494'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'project',
        sa.Column('id', sa.Integer()),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.PrimaryKeyConstraint('id'))

    op.create_table(
        'commit_',
        sa.Column('id', sa.String()),
        sa.Column('branch', sa.String(), nullable=False),
        sa.Column('pipeline_id', sa.Integer()),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('author', sa.String(), nullable=False),
        sa.Column('project_id', sa.Integer()),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.PrimaryKeyConstraint('id'))

    op.create_table(
        'job',
        sa.Column('id', sa.Integer()),
        sa.Column('job_name', sa.String(), nullable=False),
        sa.Column('start', sa.Date()),
        sa.Column('stop', sa.Date()),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('log', sa.String()),
        sa.Column('request_headers', sa.String()),
        sa.Column('request_content', sa.String()),
        sa.Column('commit_id', sa.Integer()),
        sa.ForeignKeyConstraint(['commit_id'], ['commit_.id'], ),
        sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('job')
    op.drop_table('commit_')
    op.drop_table('project')
