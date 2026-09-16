from app import create_app
from models import db, Usuario, Marca, Categoria, Producto


def seed_data():
    app = create_app('development')

    with app.app_context():
        db.create_all()

        if Usuario.query.filter_by(email='admin@keibeauty.com').first():
            print('Datos de prueba ya existen.')
            return

        admin = Usuario(
            nombre='Admin KeiBeauty',
            email='admin@keibeauty.com',
            telefono='+34600000000',
            direccion_envio='Calle Principal 123, Madrid',
            rol='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)

        marcas = [
            Marca(
                nombre='COSRX',
                descripcion='Marca coreana famosa por sus productos con centella asiatica y acido hialuronico.',
                logo_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpq4itFNV14WFJeuWpB3k11mUZ6ZRcLSlFGtHgb6A97w&s'
            ),
            Marca(
                nombre='Beauty of Joseon',
                descripcion='Marca inspirada en la belleza tradicional coreana (hanbang) con ingredientes como ginseng y arroz.',
                logo_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpq4itFNV14WFJeuWpB3k11mUZ6ZRcLSlFGtHgb6A97w&s'
            ),
            Marca(
                nombre='Some By Mi',
                descripcion='Marca coreana especializada en productos para piel sensible y con tendencia acneica.',
                logo_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpq4itFNV14WFJeuWpB3k11mUZ6ZRcLSlFGtHgb6A97w&s'
            )
        ]
        db.session.add_all(marcas)
        db.session.flush()

        categorias = [
            Categoria(
                nombre='Limpieza',
                descripcion='Limpiadores faciales, espumas, aceites y agua micelar.'
            ),
            Categoria(
                nombre='Hidratacion',
                descripcion='Cremas, geles, emulsiones y mascarillas hidratantes.'
            ),
            Categoria(
                nombre='Tratamiento',
                descripcion='Serums, ampollas, esencias y tratamientos especificos.'
            )
        ]
        db.session.add_all(categorias)
        db.session.flush()

        productos = [
            Producto(
                nombre='Low pH Good Morning Gel Cleanser',
                descripcion='Limpiador gel suave con pH bajo (5.0-6.0) que respeta la barrera cutanea. Contiene aceite de arbol de te y BHA para limpiar poros sin resecar.',
                ingredientes_clave='Aceite de arbol de te, BHA, centella asiatica',
                tipo_piel='Mixta, grasa, sensible',
                precio=14.90,
                stock=50,
                imagen_url='https://i.pinimg.com/736x/aa/0c/da/aa0cdacd84f6bd2e197a0ad37adb088c.jpg',
                estado='activo',
                marca_id=marcas[0].id,
                categoria_id=categorias[0].id
            ),
            Producto(
                nombre='Advanced Snail 96 Mucin Power Essence',
                descripcion='Esencia con 96% de mucina de caracol para reparar, hidratar y calmar la piel. Mejora la textura y elasticidad.',
                ingredientes_clave='Mucina de caracol (96%), acido hialuronico, alantoina',
                tipo_piel='Todo tipo de piel',
                precio=22.50,
                stock=40,
                imagen_url='https://i.pinimg.com/236x/76/e8/53/76e853ec56d94bb2c658298a08103c49.jpg',
                estado='activo',
                marca_id=marcas[0].id,
                categoria_id=categorias[2].id
            ),
            Producto(
                nombre='Dynasty Cream',
                descripcion='Crema nutritiva con ginseng, arroz y ceramidas. Inspirada en la belleza de la dinastia Joseon. Hidratacion profunda y efecto glow.',
                ingredientes_clave='Ginseng, agua de arroz, ceramidas, niacinamida',
                tipo_piel='Seca, normal, madura',
                precio=28.00,
                stock=30,
                imagen_url='https://i1.sndcdn.com/artworks-V5z7Q4BedhgO8DQ5-eAXCNQ-t500x500.png',
                estado='activo',
                marca_id=marcas[1].id,
                categoria_id=categorias[1].id
            ),
            Producto(
                nombre='Glow Serum Propolis + Niacinamide',
                descripcion='Serum iluminador con 60% propolis y 2% niacinamida. Controla sebo, reduce poros y unifica el tono.',
                ingredientes_clave='Propolis (60%), niacinamida (2%), extracto de curcuma',
                tipo_piel='Mixta, grasa, con manchas',
                precio=19.90,
                stock=35,
                imagen_url='https://i.pinimg.com/originals/7f/b5/13/7fb5138b4ba0a1520e6edae5f74ca923.jpg',
                estado='activo',
                marca_id=marcas[1].id,
                categoria_id=categorias[2].id
            ),
            Producto(
                nombre='AHA BHA PHA 30 Days Miracle Toner',
                descripcion='Tonico exfoliante suave con AHA, BHA y PHA. Elimina celulas muertas, controla acne y mejora textura en 30 dias.',
                ingredientes_clave='AHA, BHA, PHA, centella asiatica, arbol de te',
                tipo_piel='Grasa, acneica, textura irregular',
                precio=18.50,
                stock=45,
                imagen_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpq4itFNV14WFJeuWpB3k11mUZ6ZRcLSlFGtHgb6A97w&s',
                estado='activo',
                marca_id=marcas[2].id,
                categoria_id=categorias[2].id
            )
        ]
        db.session.add_all(productos)

        db.session.commit()
        print('Datos de prueba creados exitosamente:')
        print(f'  - 1 usuario admin (admin@keibeauty.com / admin123)')
        print(f'  - {len(marcas)} marcas')
        print(f'  - {len(categorias)} categorias')
        print(f'  - {len(productos)} productos')


if __name__ == '__main__':
    seed_data()