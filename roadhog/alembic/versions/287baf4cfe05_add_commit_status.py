"""Add commit status

Revision ID: 287baf4cfe05
Revises: beab162224e5
Create Date: 2017-09-12 10:35:24.156262

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '287baf4cfe05'
down_revision = 'beab162224e5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('commit_', sa.Column('status', sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table('commit_') as batch_op:
        batch_op.drop_column('status')
