"""Remove 'nullable' from user email and password.

Revision ID: b48aa31dcc1
Revises: b468e9cf1cc
Create Date: 2016-09-29 14:26:36.469902

"""

# revision identifiers, used by Alembic.
revision = 'b48aa31dcc1'
down_revision = 'b468e9cf1cc'

from alembic import op
from sqlalchemy.dialects import mysql


def upgrade():
    op.alter_column('user', 'email',
                    existing_type=mysql.VARCHAR(length=255),
                    nullable=False)
    op.alter_column('user', 'password',
                    existing_type=mysql.VARCHAR(length=255),
                    nullable=False)


def downgrade():
    op.alter_column('user', 'password',
                    existing_type=mysql.VARCHAR(length=255),
                    nullable=True)
    op.alter_column('user', 'email',
                    existing_type=mysql.VARCHAR(length=255),
                    nullable=True)
