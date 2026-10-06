import pymysql
from pymysql.cursors import DictCursor
import config

ESTADOS_VALIDOS = [
    "Sin aplicar",
    "En proceso (enviado)",
    "En entrevista",
    "Rechazado",
    "Oferta recibida"
]

def obtener_conexion_servidor():
    """Conecta al servidor MariaDB sin especificar base de datos (para crear la BD si no existe)."""
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        charset='utf8mb4',
        cursorclass=DictCursor,
        connect_timeout=5
    )

def obtener_conexion_bd():
    """Conecta directamente a la base de datos de postulaciones en MariaDB."""
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        charset='utf8mb4',
        cursorclass=DictCursor,
        connect_timeout=5
    )

def probar_conexion():
    """Verifica si la conexión a MariaDB y la base de datos es exitosa."""
    try:
        conn = obtener_conexion_servidor()
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION() AS version")
            version = cursor.fetchone()
        conn.close()
        return True, f"Conexión exitosa a MariaDB ({version.get('version', '')})"
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"

def inicializar_base_datos():
    """Crea la base de datos y la tabla 'aplicaciones' si no existen."""
    try:
        # 1. Asegurar la base de datos
        conn_server = obtener_conexion_servidor()
        with conn_server.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn_server.commit()
        conn_server.close()

        # 2. Asegurar la tabla de aplicaciones
        conn_db = obtener_conexion_bd()
        with conn_db.cursor() as cursor:
            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS `aplicaciones` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `empresa` VARCHAR(255) NOT NULL,
                `titulo_puesto` VARCHAR(255) NOT NULL,
                `ubicacion` VARCHAR(255) DEFAULT '',
                `url_oferta` TEXT,
                `descripcion_oferta` LONGTEXT,
                `perfil_aplicado` VARCHAR(100) DEFAULT '',
                `idioma` VARCHAR(20) DEFAULT 'es',
                `estado` VARCHAR(50) DEFAULT 'Sin aplicar',
                `asunto_correo` VARCHAR(500) DEFAULT '',
                `cuerpo_correo` LONGTEXT,
                `ruta_pdf` VARCHAR(500) DEFAULT '',
                `ruta_imagen` VARCHAR(500) DEFAULT '',
                `notas` TEXT,
                `fecha_creacion` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `fecha_actualizacion` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_estado (`estado`),
                INDEX idx_empresa (`empresa`),
                INDEX idx_fecha (`fecha_creacion`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)

            # Migración: asegurar que exista ruta_imagen si la tabla ya existía
            cursor.execute("SHOW COLUMNS FROM `aplicaciones` LIKE 'ruta_imagen'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `aplicaciones` ADD COLUMN `ruta_imagen` VARCHAR(500) DEFAULT '' AFTER `ruta_pdf`")

        conn_db.commit()
        conn_db.close()
        return True, "Base de datos inicializada correctamente"
    except Exception as e:
        return False, f"Error inicializando base de datos: {str(e)}"

def guardar_aplicacion(datos: dict) -> int:
    """Inserta una nueva aplicación de trabajo en MariaDB y retorna el ID generado."""
    conn = obtener_conexion_bd()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO aplicaciones (
                empresa, titulo_puesto, ubicacion, url_oferta, descripcion_oferta,
                perfil_aplicado, idioma, estado, asunto_correo, cuerpo_correo,
                ruta_pdf, ruta_imagen, notas, fecha_creacion, fecha_actualizacion
            ) VALUES (
                %(empresa)s, %(titulo_puesto)s, %(ubicacion)s, %(url_oferta)s, %(descripcion_oferta)s,
                %(perfil_aplicado)s, %(idioma)s, %(estado)s, %(asunto_correo)s, %(cuerpo_correo)s,
                %(ruta_pdf)s, %(ruta_imagen)s, %(notas)s, NOW(), NOW()
            )
            """
            cursor.execute(sql, {
                "empresa": datos.get("empresa", "Empresa no especificada"),
                "titulo_puesto": datos.get("titulo_puesto", "Puesto no especificado"),
                "ubicacion": datos.get("ubicacion", ""),
                "url_oferta": datos.get("url_oferta", ""),
                "descripcion_oferta": datos.get("descripcion_oferta", ""),
                "perfil_aplicado": datos.get("perfil_aplicado", ""),
                "idioma": datos.get("idioma", "es"),
                "estado": datos.get("estado", "Sin aplicar"),
                "asunto_correo": datos.get("asunto_correo", ""),
                "cuerpo_correo": datos.get("cuerpo_correo", ""),
                "ruta_pdf": datos.get("ruta_pdf", ""),
                "ruta_imagen": datos.get("ruta_imagen", ""),
                "notas": datos.get("notas", "")
            })
            nuevo_id = cursor.lastrowid
        conn.commit()
        return nuevo_id
    finally:
        conn.close()

def obtener_todas_aplicaciones(filtro_estado=None, busqueda=None) -> list:
    """Retorna la lista de aplicaciones con filtros opcionales de estado y búsqueda."""
    conn = obtener_conexion_bd()
    try:
        with conn.cursor() as cursor:
            condiciones = []
            parametros = {}

            if filtro_estado and filtro_estado != "Todos":
                condiciones.append("estado = %(estado)s")
                parametros["estado"] = filtro_estado

            if busqueda and busqueda.strip():
                condiciones.append("(empresa LIKE %(busqueda)s OR titulo_puesto LIKE %(busqueda)s OR ubicacion LIKE %(busqueda)s)")
                parametros["busqueda"] = f"%{busqueda.strip()}%"

            where_clause = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
            sql = f"SELECT * FROM aplicaciones {where_clause} ORDER BY fecha_creacion DESC;"
            cursor.execute(sql, parametros)
            return cursor.fetchall()
    finally:
        conn.close()

def obtener_aplicacion_por_id(app_id: int):
    """Retorna un registro completo por su ID."""
    conn = obtener_conexion_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM aplicaciones WHERE id = %s", (app_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def actualizar_estado_aplicacion(app_id: int, nuevo_estado: str):
    """Actualiza la fase o estado de contratación de una aplicación."""
    conn = obtener_conexion_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE aplicaciones SET estado = %s, fecha_actualizacion = NOW() WHERE id = %s",
                (nuevo_estado, app_id)
            )
        conn.commit()
        return True
    finally:
        conn.close()

def actualizar_notas_aplicacion(app_id: int, notas: str):
    """Actualiza las notas de seguimiento de una aplicación."""
    conn = obtener_conexion_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE aplicaciones SET notas = %s, fecha_actualizacion = NOW() WHERE id = %s",
                (notas, app_id)
            )
        conn.commit()
        return True
    finally:
        conn.close()

def eliminar_aplicacion(app_id: int):
    """Elimina una aplicación por su ID."""
    conn = obtener_conexion_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM aplicaciones WHERE id = %s", (app_id,))
        conn.commit()
        return True
    finally:
        conn.close()

def obtener_estadisticas_fases() -> dict:
    """Retorna el conteo de aplicaciones clasificadas por fase."""
    conn = obtener_conexion_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT estado, COUNT(*) as cantidad FROM aplicaciones GROUP BY estado")
            filas = cursor.fetchall()
            
            stats = {estado: 0 for estado in ESTADOS_VALIDOS}
            total = 0
            for f in filas:
                est = f["estado"]
                cant = f["cantidad"]
                stats[est] = cant
                total += cant
            stats["Total"] = total
            return stats
    finally:
        conn.close()
