"""initial migration

Revision ID: e04de323399d
Revises: 
Create Date: 2021-11-18 15:09:05.137464

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e04de323399d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    return
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('CareerInterest',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=64), nullable=True),
    sa.Column('num_use', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('School',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=64), nullable=True),
    sa.Column('num_use', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Swipe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('base_id', sa.Integer(), nullable=True),
    sa.Column('target_id', sa.Integer(), nullable=True),
    sa.Column('likes', sa.Boolean(), nullable=True),
    sa.Column('match', sa.Boolean(), nullable=True),
    sa.Column('shown', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=64), nullable=True),
    sa.Column('num_use', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('User',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('is_student', sa.Boolean(), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('profile_picture', sa.Text(), nullable=True),
    sa.Column('profile_picture_key', sa.Text(), nullable=True),
    sa.Column('intro_video', sa.Text(), nullable=True),
    sa.Column('intro_video_key', sa.Text(), nullable=True),
    sa.Column('email_contact', sa.Boolean(), nullable=True),
    sa.Column('phone_number', sa.String(length=64), nullable=True),
    sa.Column('city_name', sa.String(length=128), nullable=True),
    sa.Column('current_occupation', sa.String(length=128), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_User_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_User_timestamp'), ['timestamp'], unique=False)

    op.create_table('CareerInterestTag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('entered_name', sa.String(length=64), nullable=True),
    sa.Column('careerInterestID', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('EducationTag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('entered_name', sa.String(length=64), nullable=True),
    sa.Column('educationID', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('InterestTag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('entered_name', sa.String(length=64), nullable=True),
    sa.Column('interestID', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    return
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('InterestTag')
    op.drop_table('EducationTag')
    op.drop_table('CareerInterestTag')
    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_User_timestamp'))
        batch_op.drop_index(batch_op.f('ix_User_email'))

    op.drop_table('User')
    op.drop_table('Tag')
    op.drop_table('Swipe')
    op.drop_table('School')
    op.drop_table('CareerInterest')
    # ### end Alembic commands ###
