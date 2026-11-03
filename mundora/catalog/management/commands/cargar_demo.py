"""Carga un catálogo ficticio de MUNDORA sin reiniciar datos existentes."""
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils.text import slugify
from PIL import Image, ImageDraw

from catalog.models import Categoria, ImagenProducto, Producto, Tienda, Variante

GRUPO = "mundora_demo_81_propietarios"
MARCA = "Serie de demostración MUNDORA 8.1."
REGIONES = [
    ("Mendoza", "San Rafael", "5600"), ("Córdoba", "Córdoba", "5000"),
    ("Santa Fe", "Rosario", "2000"), ("Misiones", "Posadas", "3300"),
    ("Buenos Aires", "Tandil", "7000"), ("Salta", "Salta", "4400"),
    ("Río Negro", "Bariloche", "8400"), ("Chubut", "Trelew", "9100"),
]
TALLERES = ["Taller", "Estudio", "Casa", "Patio", "Galería", "Atelier", "Rincón", "Espacio", "Oficio", "Usina"]
SELLOS = ["Greda", "Umbral", "Cauce", "Níspero", "Aljibe", "Hebra", "Jarilla", "Linde", "Calandria", "Alero"]
COLORES = [("Arena", "#c3a783"), ("Oliva", "#7b875e"), ("Terracota", "#bc7154"), ("Grafito", "#555860")]
# Objeto, categoría, material, dimensiones y precio ilustrativo en ARS.
OBJETOS = [
    ("Mesa auxiliar", "Mesas", "Madera", "45 × 45 × 55 cm", 87000),
    ("Silla de comedor", "Sillas", "Madera", "44 × 48 × 82 cm", 99000),
    ("Lámina enmarcada", "Cuadros", "Papel y madera", "30 × 40 cm", 26000),
    ("Jarrón", "Jarrones", "Cerámica", "16 × 28 cm", 28500),
    ("Maceta de interior", "Macetas", "Cerámica", "20 × 22 cm", 19500),
    ("Velador", "Iluminación", "Metal y tela", "22 × 38 cm", 50000),
    ("Cortina de dos paños", "Cortinas", "Algodón", "140 × 210 cm por paño", 76000),
]
LINEAS = ["Ronda", "Surco", "Alba", "Costa", "Trama", "Bruma", "Nido", "Vega"]

def ilustracion(tipo, color):
    """Dibuja una ilustración de muestra reconocible por tipo de objeto."""
    img = Image.new("RGB", (480, 400), "#f6f2e9")
    d = ImageDraw.Draw(img)
    tinta = "#40473e"
    def forma(puntos):
        d.polygon(puntos, fill=color, outline=tinta, width=3)
    d.ellipse((78, 310, 403, 337), fill="#dfd9cd")
    if tipo in (0, 1):
        for x in (155, 305):
            d.line((x, 218, x-9, 312), fill=tinta, width=11)
        if tipo == 1:
            d.rounded_rectangle((145, 91, 327, 190), 16, fill=color, outline=tinta, width=4)
            for x in (156, 316):
                d.line((x, 184, x, 222), fill=tinta, width=8)
        d.rounded_rectangle((124, 201, 352, 229), 8, fill=color, outline=tinta, width=4)
    elif tipo == 2:
        d.rectangle((128, 72, 353, 315), fill=tinta)
        d.rectangle((138, 82, 343, 305), fill="#faf4e5")
        d.ellipse((168, 110, 247, 189), fill=color)
        forma([(150,278),(243,165),(328,278)])
    elif tipo == 3:
        forma([(210,85),(269,85),(262,145),(302,194),(309,248),(281,310),(198,310),(171,248),(178,194),(218,145)])
    elif tipo == 4:
        forma([(151,172),(329,172),(303,310),(178,310)])
        d.rectangle((142,159,338,185), fill=color, outline=tinta,width=3)
    elif tipo == 5:
        d.line((240,174,240,305), fill=tinta,width=10)
        d.ellipse((184,297,297,319),fill=tinta)
        forma([(190,84),(290,84),(325,183),(155,183)])
    else:
        d.line((96,78,384,78),fill=tinta,width=8)
        for x in (113,252):
            forma([(x,83),(x+116,83),(x+93,184),(x+111,307),(x,316)])
            for dx in (18,38,58):
                d.line((x+dx,91,x+dx-6,299),fill=tinta,width=2)
    memoria = BytesIO()
    img.save(memoria, format="JPEG", quality=86)
    return ContentFile(memoria.getvalue())

class Command(BaseCommand):
    """Completa la muestra solicitada sin sobrescribir los registros existentes."""
    help = "Crea tiendas y productos de demostración; las cantidades son totales objetivo."

    def add_arguments(self, parser):
        parser.add_argument("--tiendas", type=int, default=5)
        parser.add_argument("--productos", type=int, default=15)

    def handle(self, *args, **op):
        nt, np = op["tiendas"], op["productos"]
        if not (1 <= nt <= 100 and nt <= np <= len(OBJETOS)*len(LINEAS)*len(COLORES)):
            raise CommandError("Usá 1 a 100 tiendas y entre una publicación por tienda y 224 productos.")
        archivos = []
        try:
            with transaction.atomic():
                altas = self.cargar(nt, np, archivos)
        except Exception:
            # Los archivos de medios no participan de la transacción SQL.
            for almacen, nombre in archivos:
                almacen.delete(nombre)
            raise
        self.stdout.write(self.style.SUCCESS(
            f"Nuevas tiendas: {altas[0]}. Nuevos productos: {altas[1]}. "
            "Los registros existentes conservan su stock."
        ))

    def cargar(self, nt, np, archivos):
        """Usa identificadores reservados y distribuye las altas entre tiendas."""
        usuario = get_user_model()
        grupo, _ = Group.objects.get_or_create(name=GRUPO)
        if grupo.permissions.exists():
            raise CommandError("El grupo de demostración no debe tener permisos.")
        tiendas, nuevas, altas = [], 0, 0
        for i in range(nt):
            login = f"mundora_demo81_{i+1:03}"
            correo = f"{login}@example.invalid"
            cuenta = usuario.objects.filter(Q(username=login) | Q(email=correo)).first()
            if cuenta is None:
                cuenta = usuario.objects.create_user(username=login, email=correo, password=None)
                cuenta.groups.add(grupo)
            elif cuenta.username != login or cuenta.email != correo or not cuenta.groups.filter(pk=grupo.pk).exists():
                raise CommandError(f"Identidad ocupada fuera de la muestra: {login}.")
            provincia, localidad, cp = REGIONES[i % len(REGIONES)]
            nombre = f"{TALLERES[i//10]} {SELLOS[i%10]}"
            tienda, creada = Tienda.objects.get_or_create(propietario=cuenta, defaults=dict(
                nombre=nombre, descripcion=f"{MARCA} Taller de objetos para el hogar en {localidad}.",
                correo_contacto=correo, telefono=f"0000-{i+1:06}", provincia=provincia,
                localidad=localidad, codigo_postal=cp, calle="Pasaje de los Oficios",
                numero=str(110+i), estado=Tienda.Estado.APROBADA))
            if not tienda.descripcion.startswith(MARCA):
                raise CommandError(f"La tienda de {login} no pertenece a la muestra.")
            tiendas.append(tienda)
            nuevas += int(creada)
        cargas = {t.pk: t.productos.filter(identificador_url__startswith="demo81-p-").count() for t in tiendas}
        for i in range(np):
            slug = f"demo81-p-{i+1:04}"
            existente = Producto.objects.filter(identificador_url=slug).first()
            if existente:
                if not existente.descripcion.startswith(MARCA) or not existente.tienda.propietario.groups.filter(pk=grupo.pk).exists():
                    raise CommandError(f"Identificador ocupado: {slug}.")
                continue
            tipo = i % len(OBJETOS)
            objeto, familia, material, medidas, base = OBJETOS[tipo]
            linea = LINEAS[(i//len(OBJETOS)) % len(LINEAS)]
            tono, hexcolor = COLORES[(i//(len(OBJETOS)*len(LINEAS)) + tipo) % len(COLORES)]
            categoria, _ = Categoria.objects.get_or_create(identificador_url="demo81-"+slugify(familia),
                defaults={"nombre":familia, "descripcion": MARCA})
            if categoria.descripcion != MARCA:
                raise CommandError(f"Identificador de categoría ocupado: {familia}.")
            tienda = min(tiendas, key=lambda t: (cargas[t.pk], t.pk))
            nombre = f"{objeto} {linea} · {tono}"
            producto = Producto.objects.create(tienda=tienda, categoria=categoria, nombre=nombre,
                identificador_url=slug, descripcion=f"{MARCA} {objeto} de {material.lower()} de la línea {linea}, en tono {tono.lower()}.",
                marca=tienda.nombre, provincia_origen=tienda.provincia, publicado=True,
                estado_revision=Producto.EstadoRevision.APROBADO)
            Variante.objects.create(producto=producto, color=tono, medidas=medidas, material=material,
                precio=Decimal(base+500*(i//len(OBJETOS))), stock=3+i%13)
            foto = ImagenProducto(producto=producto, texto_alternativo=f"Ilustración de {nombre}")
            foto.imagen.save(slug+".jpg", ilustracion(tipo, hexcolor), save=False)
            archivos.append((foto.imagen.storage, foto.imagen.name))
            foto.save()
            cargas[tienda.pk] += 1
            altas += 1
        return nuevas, altas
