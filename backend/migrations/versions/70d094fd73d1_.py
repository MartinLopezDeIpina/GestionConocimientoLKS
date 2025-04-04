"""empty message

Revision ID: 70d094fd73d1
Revises: c72cccf7099d
Create Date: 2024-06-28 10:39:07.433892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70d094fd73d1'
down_revision = 'c72cccf7099d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('conocimiento_usuario',
    sa.Column('usuario_email', sa.String(length=250), nullable=False),
    sa.Column('nodoID', sa.Integer(), nullable=False),
    sa.Column('nivel_IA', sa.Integer(), nullable=True),
    sa.Column('nivel_validado', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['nodoID'], ['nodo_arbol.nodoID'], ),
    sa.ForeignKeyConstraint(['usuario_email'], ['usuario.email'], ),
    sa.PrimaryKeyConstraint('usuario_email', 'nodoID')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('conocimiento_usuario')
    # ### end Alembic commands ###
