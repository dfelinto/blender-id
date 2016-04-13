"""Merge subclient and regular tokens.

Revision ID: 15c3f600013
Revises: 10b00e658d8
Create Date: 2016-04-13 13:44:01.191760

"""

# revision identifiers, used by Alembic.
revision = '15c3f600013'
down_revision = '10b00e658d8'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.drop_table('subclient_token')
    op.add_column('token', sa.Column('subclient', sa.String(length=40), nullable=True))


def downgrade():
    op.drop_column('token', 'subclient')
    op.create_table('subclient_token',
                    sa.Column('subclient_specific_token', mysql.VARCHAR(length=32), nullable=False),
                    sa.Column('client_id', mysql.VARCHAR(length=40), nullable=False),
                    sa.Column('subclient_id', mysql.VARCHAR(length=40), nullable=False),
                    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False,
                              nullable=False),
                    sa.Column('expires', mysql.DATETIME(), nullable=True),
                    sa.Column('host_label', mysql.VARCHAR(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['client_id'], [u'client.client_id'],
                                            name=u'subclient_token_ibfk_1'),
                    sa.ForeignKeyConstraint(['user_id'], [u'user.id'],
                                            name=u'subclient_token_ibfk_2'),
                    sa.PrimaryKeyConstraint('subclient_specific_token'),
                    mysql_default_charset=u'utf8',
                    mysql_engine=u'InnoDB'
                    )
