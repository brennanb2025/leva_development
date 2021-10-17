"""added career interest, interest, education

Revision ID: a4d710ab784b
Revises: 
Create Date: 2021-02-16 18:11:38.894425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4d710ab784b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('User',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('is_teacher', sa.Boolean(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_User_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_User_timestamp'), ['timestamp'], unique=False)

    op.create_table('CareerInterestTag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('careerInterestID', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('EducationTag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('educationID', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('InterestTag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('interestID', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('CareerInterest',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('careerInterestID', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['careerInterestID'], ['CareerInterestTag.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('School',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('schoolID', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['schoolID'], ['EducationTag.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tagID', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['tagID'], ['InterestTag.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Tag')
    op.drop_table('School')
    op.drop_table('CareerInterest')
    op.drop_table('InterestTag')
    op.drop_table('EducationTag')
    op.drop_table('CareerInterestTag')
    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_User_timestamp'))
        batch_op.drop_index(batch_op.f('ix_User_email'))

    op.drop_table('User')
    # ### end Alembic commands ###
