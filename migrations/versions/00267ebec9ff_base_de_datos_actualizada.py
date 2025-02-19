"""Base de datos actualizada

Revision ID: 00267ebec9ff
Revises: 
Create Date: 2025-02-18 21:28:16.718264

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2

# revision identifiers, used by Alembic.
revision = '00267ebec9ff'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('datalogers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=255), nullable=False),
    sa.Column('ip', sa.String(length=50), nullable=False),
    sa.Column('api_token', sa.String(length=255), nullable=False),
    sa.Column('api_url', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('escuelas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=255), nullable=False),
    sa.Column('comuna', sa.String(length=255), nullable=False),
    sa.Column('director', sa.String(length=255), nullable=True),
    sa.Column('profesor', sa.String(length=255), nullable=True),
    sa.Column('curso', sa.String(length=255), nullable=True),
    sa.Column('coordenadas', geoalchemy2.types.Geometry(geometry_type='POINT', from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('escuelas', schema=None) as batch_op:
        batch_op.create_index('idx_escuelas_coordenadas', ['coordenadas'], unique=False, postgresql_using='gist')

    op.create_table('plantas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('especie', sa.String(length=100), nullable=False),
    sa.Column('fecha_plantado', sa.Date(), nullable=True),
    sa.Column('fecha_cosecha', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('variables',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=255), nullable=False),
    sa.Column('unidad_medida', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mediciones_bajadas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('datetime', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('valor', sa.Float(), nullable=False),
    sa.Column('precision', sa.Float(), nullable=True),
    sa.Column('id_dataloger', sa.Integer(), nullable=True),
    sa.Column('id_planta', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_dataloger'], ['datalogers.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_planta'], ['plantas.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('modulos_escolares',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=255), nullable=False),
    sa.Column('ubicacion', sa.String(length=255), nullable=True),
    sa.Column('coordenadas', geoalchemy2.types.Geometry(geometry_type='POINT', from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
    sa.Column('id_dataloger', sa.Integer(), nullable=True),
    sa.Column('id_planta', sa.Integer(), nullable=True),
    sa.Column('id_escuela', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_dataloger'], ['datalogers.id'], ),
    sa.ForeignKeyConstraint(['id_escuela'], ['escuelas.id'], ),
    sa.ForeignKeyConstraint(['id_planta'], ['plantas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('modulos_escolares', schema=None) as batch_op:
        batch_op.create_index('idx_modulos_escolares_coordenadas', ['coordenadas'], unique=False, postgresql_using='gist')

    op.create_table('planta_variable',
    sa.Column('id_planta', sa.Integer(), nullable=False),
    sa.Column('id_variable', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_planta'], ['plantas.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_variable'], ['variables.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_planta', 'id_variable')
    )
    op.create_table('rangos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('temperatura_min', sa.Float(), nullable=True),
    sa.Column('temperatura_max', sa.Float(), nullable=True),
    sa.Column('ph_min', sa.Float(), nullable=True),
    sa.Column('ph_max', sa.Float(), nullable=True),
    sa.Column('humedad_min', sa.Float(), nullable=True),
    sa.Column('humedad_max', sa.Float(), nullable=True),
    sa.Column('id_planta', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_planta'], ['plantas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rangos')
    op.drop_table('planta_variable')
    with op.batch_alter_table('modulos_escolares', schema=None) as batch_op:
        batch_op.drop_index('idx_modulos_escolares_coordenadas', postgresql_using='gist')

    op.drop_table('modulos_escolares')
    op.drop_table('mediciones_bajadas')
    op.drop_table('variables')
    op.drop_table('plantas')
    with op.batch_alter_table('escuelas', schema=None) as batch_op:
        batch_op.drop_index('idx_escuelas_coordenadas', postgresql_using='gist')

    op.drop_table('escuelas')
    op.drop_table('datalogers')
    # ### end Alembic commands ###
