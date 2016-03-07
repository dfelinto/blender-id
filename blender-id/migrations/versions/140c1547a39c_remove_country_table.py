"""Remove now-unused country table.

Revision ID: 140c1547a39c
Revises: 318bd98a6ad1
Create Date: 2016-03-07 13:41:56.406010

"""

# revision identifiers, used by Alembic.
revision = '140c1547a39c'
down_revision = '318bd98a6ad1'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.drop_table('country')


def downgrade():
    op.create_table('country',
                    sa.Column('id', mysql.INTEGER(display_width=5), nullable=False),
                    sa.Column('code', mysql.CHAR(length=2), server_default=sa.text(u"''"), nullable=False),
                    sa.Column('name', mysql.VARCHAR(length=45), server_default=sa.text(u"''"), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    mysql_default_charset=u'utf8',
                    mysql_engine=u'InnoDB'
                    )
