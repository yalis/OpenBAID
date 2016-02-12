import logging
import os
import simplejson
import sys

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from accounts.models import Localidad, Nacionalidad,\
    Provincia, TipoDocumento

reload(sys)
sys.setdefaultencoding("utf-8")

MIGRATION_DIR = os.path.join(settings.BASE_DIR, 'initial_data/')
NACIONALIDAD = 'nacionalidad.json'
TIPOS_DOCUMENTOS = 'tipos_documentos.json'
PROVINCIAS = 'provincias.json'
LOCALIDADES = 'localidades.json'
GENEROS = 'generos.json'

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Carga la informacion por defecto en la base de datos"""

    def handle(self, *args, **options):
        """ Maneja el comando para exportar usuarios """

        try:
            msg = "Creando grupo por defecto oauth"
            self.stdout.write(msg)
            Group.objects.get_or_create(name='oauth')
            msg = "Cargando informacion de: {}".format(MIGRATION_DIR)
            self.stdout.write(msg)
            nacionalidades = self.abrir_archivo(NACIONALIDAD)
            nacionalidad_buffer = []
            tipo_documento_buffer = []
            provincias_buffer = []
            localidades_buffer = []

            counter = 1
            self.stdout.write("\nCargando nacionalidades")
            if Nacionalidad.objects.count() == 0:
                for nacionalidad in nacionalidades:
                    sys.stdout.write("\rNacionalidades:{}".format(counter))
                    sys.stdout.flush()
                    nacionalidad_buffer.append(
                        Nacionalidad(nombre=nacionalidad['name'],
                                     codigo=nacionalidad['code']))
                    counter += 1
                Nacionalidad.objects.bulk_create(nacionalidad_buffer)
            else:
                msg = "No se cargan nacionalidades.Ya hay registros"
                self.stdout.write(msg)

            tipo_documentos = self.abrir_archivo(TIPOS_DOCUMENTOS)
            self.stdout.write("\nCargando tipo documento")
            if TipoDocumento.objects.count() == 0:
                counter = 1
                for tipo_doc in tipo_documentos:
                    sys.stdout.write("\rTipo documento:{}".format(counter))
                    sys.stdout.flush()
                    tipo_documento_buffer.append(TipoDocumento(tipo=tipo_doc))
                    counter += 1
                TipoDocumento.objects.bulk_create(tipo_documento_buffer)
            else:
                msg = "No se carga tipo de documento, ya habia registros"
                self.stdout.write(msg)

            self.stdout.write("\nCargando provincias")
            if Provincia.objects.count() == 0:
                provincias = self.abrir_archivo(PROVINCIAS)
                counter = 1
                for provincia in provincias:
                    counter += 1
                    sys.stdout.write("\rProvincias:{}".format(counter))
                    sys.stdout.flush()
                    provincias_buffer.append(
                        Provincia(nombre=provincia['nombre'],
                                  id=provincia['id']))
                Provincia.objects.bulk_create(provincias_buffer)
            else:
                msg = "No se cargan provincias.Ya habia provincias cargadas"
                self.stdout.write(msg)

            self.stdout.write("\nCargando localidades")
            localidades = self.abrir_archivo(LOCALIDADES)
            counter = 1
            if Localidad.objects.count() == 0:
                for localidad in localidades:
                    sys.stdout.write("\rLocalidades:{}".format(counter))
                    sys.stdout.flush()
                    provincia_id = localidad['id_provincia']
                    provincia = Provincia.objects.filter(id=provincia_id).get()
                    loc = Localidad(nombre=localidad['nombre'].encode('utf-8'),
                                    provincia=provincia)
                    localidades_buffer.append(loc)
                    counter += 1
                Localidad.objects.bulk_create(localidades_buffer)
            else:
                msg = "No se cargan localidades, ya habia registros"
                self.stdout.write(msg)

        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            msg = "Error: {0}, {1}, {2}".format(exc_type, fname,
                                                exc_tb.tb_lineno)
            self.stdout.write(msg)

    def abrir_archivo(self, archivo):
        try:
            input_file = None
            full_path = os.path.join(MIGRATION_DIR, archivo)
            input_file = open(full_path, 'rb')
            content = simplejson.loads(input_file.read())
        except Exception as e:
            msg = "Tuvimos un error abriendo los archivos. {}".format(e)
            logger.error(msg)
        finally:
            if input_file is not None:
                input_file.close()
            return content
