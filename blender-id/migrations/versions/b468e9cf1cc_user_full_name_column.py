"""User full_name column

Revision ID: b468e9cf1cc
Revises: 15c3f600013
Create Date: 2016-06-30 07:51:01.747550

"""

# revision identifiers, used by Alembic.
revision = 'b468e9cf1cc'
down_revision = '15c3f600013'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


def upgrade():
    # We would like full_name to be NOT NULL in the future
    op.add_column('user', sa.Column(
        'full_name', sa.String(length=255)))
    conn = op.get_bind()
    query = "UPDATE user SET full_name = CONCAT(first_name, ' ', last_name)"
    conn.execute(text(query))


def downgrade():
    op.drop_column('user', 'full_name')
