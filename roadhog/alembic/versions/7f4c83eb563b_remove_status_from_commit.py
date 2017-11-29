"""Remove status from commit

Revision ID: 7f4c83eb563b
Revises: ff9aa80970e9
Create Date: 2017-11-29 15:07:22.317605

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f4c83eb563b'
down_revision = 'ff9aa80970e9'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('commit_') as batch_op:
        batch_op.drop_column('status')

def downgrade():
    op.add_column('commit_', sa.Column('status', sa.String(), nullable=True))
