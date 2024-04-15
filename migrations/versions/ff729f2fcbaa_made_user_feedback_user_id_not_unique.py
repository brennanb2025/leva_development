"""Made user feedback user id not unique

Revision ID: ff729f2fcbaa
Revises: 0e665f20559a
Create Date: 2024-04-14 22:59:52.073234

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff729f2fcbaa'
down_revision = '0e665f20559a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('UserFeedback', schema=None) as batch_op:
        batch_op.drop_index('ix_UserFeedback_user_id')
        batch_op.create_index(batch_op.f('ix_UserFeedback_user_id'), ['user_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('UserFeedback', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_UserFeedback_user_id'))
        batch_op.create_index('ix_UserFeedback_user_id', ['user_id'], unique=1)

    # ### end Alembic commands ###
