"""added mentor_gender_preference, gender_identity, division_preference, and personality 1, 2, and 3

Revision ID: 9dfd7fa5d79d
Revises: 6f0efddfc806
Create Date: 2021-12-27 18:06:13.409662

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9dfd7fa5d79d'
down_revision = '6f0efddfc806'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.add_column(sa.Column('division_preference', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('gender_identity', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('mentor_gender_preference', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('personality_1', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('personality_2', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('personality_3', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.drop_column('personality_3')
        batch_op.drop_column('personality_2')
        batch_op.drop_column('personality_1')
        batch_op.drop_column('mentor_gender_preference')
        batch_op.drop_column('gender_identity')
        batch_op.drop_column('division_preference')

    # ### end Alembic commands ###
