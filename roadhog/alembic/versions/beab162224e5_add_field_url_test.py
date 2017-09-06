"""add field url test

Revision ID: beab162224e5
Revises: cda54b3bb494
Create Date: 2017-09-06 11:50:35.886457

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'beab162224e5'
down_revision = 'cda54b3bb494'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('commit_', sa.Column('url_test', sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table('commit_') as batch_op:
        batch_op.drop_column('url_test')
#     op.drop_column('commit_', 'url_test')
