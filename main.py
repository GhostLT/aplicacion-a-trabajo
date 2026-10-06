import sys
import os
import database
import profile_data
from ui.app_window import MainWindow

def main():
    print("=========================================================")
    print("  PostulaPro - Generador de CVs ATS y Gestor de Empleo  ")
    print("  Javier Viveros Huesca | MariaDB | Edge Headless PDF   ")
    print("=========================================================")

    # 1. Asegurar base de datos MariaDB
    print("\n[1/3] Verificando base de datos MariaDB...")
    ok_db, msg_db = database.inicializar_base_datos()
    if ok_db:
        print(f"  -> MariaDB OK: {msg_db}")
    else:
        print(f"  -> ADVERTENCIA: {msg_db}")
        print("  -> Puedes configurar tus credenciales en la pestaña 'Configuración'.")

    # 2. Cargar perfil base
    print("\n[2/3] Cargando perfil base del candidato...")
    perfil = profile_data.load_user_profile()
    nombre = perfil.get("datos_personales", {}).get("nombre", "Usuario")
    print(f"  -> Perfil cargado: {nombre}")

    # 3. Lanzar interfaz gráfica Tkinter
    print("\n[3/3] Iniciando interfaz gráfica Tkinter...")
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
