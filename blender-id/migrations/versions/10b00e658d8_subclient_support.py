"""Add subclient-specific token support.

Revision ID: 10b00e658d8
Revises: 140c1547a39c
Create Date: 2016-04-08 10:24:24.972444

"""

# revision identifiers, used by Alembic.
revision = '10b00e658d8'
down_revision = '140c1547a39c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.alter_column('token', 'user_id',
                    existing_type=mysql.INTEGER(display_width=11),
                    nullable=False)
    op.create_table('subclient_token',
                    sa.Column('subclient_specific_token', sa.String(length=32), nullable=False),
                    sa.Column('client_id', sa.String(length=40), nullable=False),
                    sa.Column('subclient_id', sa.String(length=40), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('expires', sa.DateTime(), nullable=True),
                    sa.Column('host_label', sa.String(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['client_id'], ['client.client_id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('subclient_specific_token')
                    )


def downgrade():
    op.drop_table('subclient_token')
    op.alter_column('token', 'user_id',
                    existing_type=mysql.INTEGER(display_width=11),
                    nullable=True)
