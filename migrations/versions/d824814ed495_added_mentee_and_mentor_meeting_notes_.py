"""added mentee and mentor meeting notes to select, also added current meeting number for both mentor and mentee to select

Revision ID: d824814ed495
Revises: 112dcfa42b0b
Create Date: 2022-05-19 16:34:55.315388

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd824814ed495'
down_revision = '112dcfa42b0b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Select', schema=None) as batch_op:
        batch_op.add_column(sa.Column('current_meeting_number_mentee', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('current_meeting_number_mentor', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('mentee_meeting_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('mentor_meeting_notes', sa.Text(), nullable=True))
        batch_op.drop_column('current_meeting_ID')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Select', schema=None) as batch_op:
        batch_op.add_column(sa.Column('current_meeting_ID', mysql.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_column('mentor_meeting_notes')
        batch_op.drop_column('mentee_meeting_notes')
        batch_op.drop_column('current_meeting_number_mentor')
        batch_op.drop_column('current_meeting_number_mentee')

    # ### end Alembic commands ###