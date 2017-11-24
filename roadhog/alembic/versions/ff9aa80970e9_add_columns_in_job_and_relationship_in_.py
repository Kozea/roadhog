"""Add columns in job and relationship in project

Revision ID: ff9aa80970e9
Revises: 287baf4cfe05
Create Date: 2017-10-19 15:17:56.355747

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff9aa80970e9'
down_revision = '287baf4cfe05'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'commit_', sa.Column('commit_date', sa.DateTime()))
    op.add_column(
        'commit_', sa.Column('coverage', sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table('commit_') as batch_op:
        batch_op.drop_column('coverage')
        batch_op.drop_column('commit_date')
