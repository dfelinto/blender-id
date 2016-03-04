"""add host_label to OAuth Token

Revision ID: 318bd98a6ad1
Revises: 5ad8402012cc
Create Date: 2016-03-02 16:45:47.273081

"""

# revision identifiers, used by Alembic.
revision = '318bd98a6ad1'
down_revision = '5ad8402012cc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('token', sa.Column('host_label', sa.String(length=255)))


def downgrade():
    op.drop_column('token', 'host_label')
