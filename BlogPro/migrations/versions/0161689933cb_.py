"""empty message

Revision ID: 0161689933cb
Revises: ea7e6f1549b4
Create Date: 2019-05-21 13:31:05.550106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0161689933cb'
down_revision = 'ea7e6f1549b4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.Column('passwd', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
