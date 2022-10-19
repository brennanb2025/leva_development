"""added events, also changed feed to store match info

Revision ID: ff13e9fa4189
Revises: 420c7f884bef
Create Date: 2022-02-19 20:30:29.978294

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff13e9fa4189'
down_revision = '420c7f884bef'
branch_labels = None
depends_on = None


"""
SKIP THIS - 
Related to head error I assume. Identical to 420c7f884bef.
"""

def upgrade():
    return
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userID', sa.Integer(), nullable=True),
    sa.Column('action', sa.Integer(), nullable=True),
    sa.Column('message', sa.String(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('Event', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_Event_timestamp'), ['timestamp'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    return
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Event', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_Event_timestamp'))

    op.drop_table('Event')
    # ### end Alembic commands ###
