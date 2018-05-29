"""empty message

Revision ID: 8e615c208ab6
Revises: 8c87a163c2ae
Create Date: 2018-04-20 05:17:21.670162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e615c208ab6'
down_revision = '8c87a163c2ae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comparisons',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('analysis_filename', sa.String(), nullable=True),
    sa.Column('analysis_filepath', sa.String(), nullable=True),
    sa.Column('manual_filename', sa.String(), nullable=True),
    sa.Column('manual_filepath', sa.String(), nullable=True),
    sa.Column('body', sa.String(), nullable=True),
    sa.Column('score', sa.String(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comparisons')
    # ### end Alembic commands ###
