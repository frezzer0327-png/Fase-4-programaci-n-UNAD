from abc import ABC, abstractmethod
from datetime import datetime

# Desarrollo: parte 1: Sistema de registro de eventos y errores Archivo de Logs

class RegistradorLogs:
    """
    Esta clase se encarga únicamente de escribir en un archivo de texto
    todo lo que pasa en el sistema (eventos normales y errores).
    No usamos bases de datos, solo este archivo de logs como pide el anexo.
    """
    def __init__(self, nombre_archivo="logs_software_fj.txt"):
        # Guardamos el nombre del archivo de forma privada con guion bajo.
        self._nombre_archivo = nombre_archivo

    def registrar(self, tipo, mensaje):
        # Obtenemos la fecha y hora exacta en la que ocurrió el evento.
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{fecha_hora}] [{tipo}] {mensaje}\n"

        # Usamos try/except/finally para asegurar que si hay un problema al abrir
        # el archivo, el programa principal no se caiga.
        archivo = None
        try:
            archivo = open(self._nombre_archivo, "a", encoding="utf-8")
            archivo.write(linea)
        except OSError as error:
            print(f"Error crítico al escribir en el log: {error}")
        finally:
            # El bloque finally siempre se ejecuta para garantizar que el archivo se cierre.
            if archivo is not None:
                archivo.close()
# Creamos una instancia global del registrador para usarla en todo el sistema.
logger = RegistradorLogs()
# Desarrollo: parte 2: Excepciones Personalizadas
# Creamos una clase base para todas las excepciones de nuestra empresa Software FJ.
class ErrorSistemaFJ(Exception):
    pass
# Se lanza cuando un dato tiene un formato incorrecto (ej. correo sin @ o precio negativo).
class DatoInvalidoError(ErrorSistemaFJ):
    pass


# Se lanza cuando falta un dato obligatorio (ej. nombre vacío o nulo).
class ParametroFaltanteError(ErrorSistemaFJ):
    pass


# Se lanza cuando se intenta hacer algo que el estado actual no permite (ej. confirmar algo ya cancelado).
class OperacionNoPermitidaError(ErrorSistemaFJ):
    pass


# Se lanza cuando el servicio que se intenta reservar está marcado como no disponible.
class ServicioNoDisponibleError(ErrorSistemaFJ):
    pass


# Se lanza cuando un cálculo matemático no tiene sentido (ej. descuento mayor al 100%).
class CalculoInconsistenteError(ErrorSistemaFJ):
    pass


# Se lanza cuando falla el procesamiento general de una reserva (la usaremos para encadenar errores).
class ReservaError(ErrorSistemaFJ):
    pass
# Desarrollo: parte 3: Clase Abstracta Entidad (Base de todo el sistema)

class Entidad(ABC):
    def __init__(self, id_entidad):
        # Validamos que toda entidad tenga un identificador antes de crearse.
        if not id_entidad or not str(id_entidad).strip():
            raise ParametroFaltanteError("El ID de la entidad es obligatorio y no puede estar vacío.")

        # Atributos privados (encapsulación) para proteger los datos internos.
        self._id_entidad = str(id_entidad).strip()
        self._fecha_creacion = datetime.now()

    @property
    def id_entidad(self):
        return self._id_entidad

    @property
    def fecha_creacion(self):
        return self._fecha_creacion

    # Métodos abstractos: obligan a todas las clases hijas a implementarlos.
    @abstractmethod
    def validar(self):
        pass

    @abstractmethod
    def obtener_resumen(self):
        pass
# Desarrollo: parte 4: Clase Cliente (Encapsulación y Validaciones Robustas)

class Cliente(Entidad):
    def __init__(self, id_entidad, nombre, documento, correo, telefono):
        # Llamamos al constructor de la clase padre Entidad.
        super().__init__(id_entidad)

        # Guardamos los datos personales como atributos privados.
        self._nombre = nombre
        self._documento = documento
        self._correo = correo
        self._telefono = telefono

        # Ejecutamos la validación apenas se intenta crear el cliente.
        self.validar()

    # Getters para leer los datos privados sin exponer directamente los atributos.
    @property
    def nombre(self):
        return self._nombre

    @property
    def documento(self):
        return self._documento

    @property
    def correo(self):
        return self._correo

    @property
    def telefono(self):
        return self._telefono

    def validar(self):
        # Revisamos que ningún campo obligatorio venga vacío.
        if not self._nombre or not str(self._nombre).strip():
            raise ParametroFaltanteError("El nombre del cliente es obligatorio.")
        if not self._documento or not str(self._documento).strip():
            raise ParametroFaltanteError("El documento del cliente es obligatorio.")
        if not self._correo or not str(self._correo).strip():
            raise ParametroFaltanteError("El correo electrónico es obligatorio.")

        # Validamos el formato del documento (solo números y mínimo 6 dígitos).
        if not str(self._documento).isdigit() or len(str(self._documento)) < 6:
            raise DatoInvalidoError(f"El documento '{self._documento}' debe tener al menos 6 dígitos numéricos.")

        # Validamos que el correo tenga un formato básico válido (@ y punto).
        if "@" not in self._correo or "." not in self._correo:
            raise DatoInvalidoError(f"El correo '{self._correo}' no tiene un formato válido.")

        # Validamos que el teléfono sea numérico y tenga al menos 7 dígitos.
        if not str(self._telefono).isdigit() or len(str(self._telefono)) < 7:
            raise DatoInvalidoError(f"El teléfono '{self._telefono}' debe ser numérico y tener al menos 7 dígitos.")

    def obtener_resumen(self):
        return f"Cliente [{self._id_entidad}] {self._nombre} | Doc: {self._documento} | Correo: {self._correo}"

# Desarrollo: parte 5: Clase Abstracta Servicio y 3 Servicios Especializados
# (Herencia, Polimorfismo y Sobrecarga de Métodos)
# =============================================================================

class Servicio(Entidad, ABC):
    def __init__(self, id_entidad, nombre, tarifa_base, disponible=True):
        super().__init__(id_entidad)
        self._nombre = nombre
        self._tarifa_base = tarifa_base
        self._disponible = disponible
        self.validar()

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_base(self):
        return self._tarifa_base

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, estado):
        if not isinstance(estado, bool):
            raise DatoInvalidoError("La disponibilidad debe ser un valor booleano (True o False).")
        self._disponible = estado

    def validar(self):
        if not self._nombre or not str(self._nombre).strip():
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        if not isinstance(self._tarifa_base, (int, float)) or self._tarifa_base <= 0:
            raise DatoInvalidoError(f"La tarifa base ({self._tarifa_base}) debe ser un número mayor que cero.")

    # Método sobrecargado:
    # En Python no se pueden crear dos funciones con el mismo nombre, entonces para hacer
    # la sobrecarga le ponemos valores por defecto (=0). Así la función sirve si le mandamos
    # solo la duración, o si le mandamos duración + descuento, o duración + descuento + impuesto + cargo extra.
    def calcular_costo(self, duracion, descuento=0, impuesto=0, cargo_extra=0):
        self.validar_parametros(duracion)

        # Validamos que los porcentajes y cargos tengan sentido matemático.
        if descuento < 0 or descuento > 100:
            raise CalculoInconsistenteError(f"El descuento ({descuento}%) debe estar entre 0% y 100%.")
        if impuesto < 0 or impuesto > 50:
            raise CalculoInconsistenteError(f"El impuesto ({impuesto}%) está fuera de un rango válido (0% - 50%).")
        if cargo_extra < 0:
            raise CalculoInconsistenteError("El cargo extra no puede ser negativo.")

        subtotal = (self._tarifa_base * duracion) + cargo_extra
        valor_descuento = subtotal * (descuento / 100)
        base_gravable = subtotal - valor_descuento
        valor_impuesto = base_gravable * (impuesto / 100)
        total = base_gravable + valor_impuesto

        if total < 0:
            raise CalculoInconsistenteError("El cálculo arrojó un total negativo, lo cual es inconsistente.")

        return round(total, 2)

    @abstractmethod
    def describir_servicio(self):
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    def obtener_resumen(self):
        return self.describir_servicio()


# --- Servicio Especializado 1: Reserva de Salas ---
class ReservaSala(Servicio):
    def __init__(self, id_entidad, nombre, tarifa_base, capacidad, incluye_proyector=False, disponible=True):
        self._capacidad = capacidad
        self._incluye_proyector = incluye_proyector
        super().__init__(id_entidad, nombre, tarifa_base, disponible)

    def validar(self):
        super().validar()
        if not isinstance(self._capacidad, int) or self._capacidad <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser un entero positivo.")

    def validar_parametros(self, duracion):
        # Las salas se alquilan por horas (mínimo 1 hora, máximo 12 horas seguidas).
        if not isinstance(duracion, (int, float)) or duracion <= 0 or duracion > 12:
            raise DatoInvalidoError("La duración para reserva de sala debe ser entre 1 y 12 horas.")

    def calcular_costo(self, duracion, descuento=0, impuesto=0, cargo_extra=0):
        # Polimorfismo: si la sala incluye proyector, sumamos un cargo fijo de $20.000.
        extra_proyector = 20000 if self._incluye_proyector else 0
        return super().calcular_costo(duracion, descuento, impuesto, cargo_extra + extra_proyector)

    def describir_servicio(self):
        proyector = "Sí" if self._incluye_proyector else "No"
        return (f"Sala '{self._nombre}' | Tarifa/h: ${self._tarifa_base:,.2f} | "
                f"Capacidad: {self._capacidad} personas | Proyector: {proyector}")


# --- Servicio Especializado 2: Alquiler de Equipos ---
class AlquilerEquipo(Servicio):
    def __init__(self, id_entidad, nombre, tarifa_base, tipo_equipo, cantidad_equipos=1, disponible=True):
        self._tipo_equipo = tipo_equipo
        self._cantidad_equipos = cantidad_equipos
        super().__init__(id_entidad, nombre, tarifa_base, disponible)

    def validar(self):
        super().validar()
        if not self._tipo_equipo or not str(self._tipo_equipo).strip():
            raise ParametroFaltanteError("El tipo de equipo es obligatorio.")
        if not isinstance(self._cantidad_equipos, int) or self._cantidad_equipos <= 0:
            raise DatoInvalidoError("La cantidad de equipos debe ser un entero mayor que cero.")

    def validar_parametros(self, duracion):
        # Los equipos se alquilan por días (mínimo 1 día, máximo 30 días).
        if not isinstance(duracion, int) or duracion <= 0 or duracion > 30:
            raise DatoInvalidoError("La duración para alquiler de equipos debe ser un entero entre 1 y 30 días.")

    def calcular_costo(self, duracion, descuento=0, impuesto=0, cargo_extra=0):
        # Polimorfismo: multiplicamos la duración por la cantidad de equipos alquilados.
        duracion_total = duracion * self._cantidad_equipos
        # Validamos primero la duración real en días antes de multiplicar.
        self.validar_parametros(duracion)
        subtotal = (self._tarifa_base * duracion_total) + cargo_extra
        if descuento < 0 or descuento > 100:
            raise CalculoInconsistenteError(f"El descuento ({descuento}%) debe estar entre 0% y 100%.")
        if impuesto < 0 or impuesto > 50:
            raise CalculoInconsistenteError(f"El impuesto ({impuesto}%) está fuera de rango.")
        total = (subtotal - (subtotal * descuento / 100)) * (1 + impuesto / 100)
        return round(total, 2)

    def describir_servicio(self):
        return (f"Alquiler '{self._nombre}' ({self._tipo_equipo}) | Tarifa/día: ${self._tarifa_base:,.2f} | "
                f"Cantidad: {self._cantidad_equipos} und.")


# --- Servicio Especializado 3: Asesorías Especializadas ---
class AsesoriaEspecializada(Servicio):
    def __init__(self, id_entidad, nombre, tarifa_base, area_tematica, modalidad="Virtual", disponible=True):
        self._area_tematica = area_tematica
        self._modalidad = modalidad
        super().__init__(id_entidad, nombre, tarifa_base, disponible)

    def validar(self):
        super().validar()
        if not self._area_tematica or not str(self._area_tematica).strip():
            raise ParametroFaltanteError("El área temática de la asesoría es obligatoria.")
        if self._modalidad not in ("Virtual", "Presencial"):
            raise DatoInvalidoError("La modalidad debe ser 'Virtual' o 'Presencial'.")

    def validar_parametros(self, duracion):
        # Las asesorías se cobran por horas (entre 1 y 8 horas).
        if not isinstance(duracion, (int, float)) or duracion < 1 or duracion > 8:
            raise DatoInvalidoError("La duración de la asesoría debe estar entre 1 y 8 horas.")

    def calcular_costo(self, duracion, descuento=0, impuesto=0, cargo_extra=0):
        # Polimorfismo: si la asesoría es presencial, se suma un recargo logístico de $35.000.
        recargo_viaticos = 35000 if self._modalidad == "Presencial" else 0
        return super().calcular_costo(duracion, descuento, impuesto, cargo_extra + recargo_viaticos)

    def describir_servicio(self):
        return (f"Asesoría '{self._nombre}' | Área: {self._area_tematica} | "
                f"Modalidad: {self._modalidad} | Tarifa/h: ${self._tarifa_base:,.2f}")


# Desarrollo: parte 6: Clase Reserva (Estados, Procesamiento y Encadenamiento)

class Reserva(Entidad):
    def __init__(self, id_entidad, cliente, servicio, duracion):
        super().__init__(id_entidad)
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._estado = "PENDIENTE"
        self._costo_total = 0.0
        self.validar()

    @property
    def estado(self):
        return self._estado

    @property
    def costo_total(self):
        return self._costo_total

    def validar(self):
        if not isinstance(self._cliente, Cliente):
            raise DatoInvalidoError("La reserva debe estar asociada a un objeto Cliente válido.")
        if not isinstance(self._servicio, Servicio):
            raise DatoInvalidoError("La reserva debe estar asociada a un objeto Servicio válido.")
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{self._servicio.nombre}' no está disponible actualmente.")
        # Validamos que la duración cumpla con las reglas del servicio específico.
        self._servicio.validar_parametros(self._duracion)

    def procesar(self, descuento=0, impuesto=19, cargo_extra=0):
        # Aquí usamos try/except/else/finally y encadenamiento de excepciones (raise ... from e).
        try:
            if self._estado == "CANCELADA":
                raise OperacionNoPermitidaError("No se puede procesar una reserva que ya fue cancelada.")
            self._costo_total = self._servicio.calcular_costo(
                self._duracion, descuento=descuento, impuesto=impuesto, cargo_extra=cargo_extra
            )
        except ErrorSistemaFJ as error_original:
            # Encadenamos la excepción original dentro de una ReservaError para no perder el rastro.
            logger.registrar("ERROR", f"Fallo al procesar reserva {self._id_entidad}: {error_original}")
            raise ReservaError(f"No fue posible procesar la reserva {self._id_entidad}.") from error_original
        else:
            # El bloque else solo se ejecuta si el try terminó sin ningún error.
            logger.registrar(
                "INFO",
                f"Reserva {self._id_entidad} procesada con éxito. Total: ${self._costo_total:,.2f}"
            )
            return self._costo_total
        finally:
            # El bloque finally siempre se ejecuta, haya error o no.
            logger.registrar("EVENTO", f"Intento de procesamiento finalizado para reserva {self._id_entidad}.")

    def confirmar(self):
        if self._estado == "CANCELADA":
            raise OperacionNoPermitidaError(f"La reserva {self._id_entidad} está cancelada y no puede confirmarse.")
        if self._estado == "CONFIRMADA":
            raise OperacionNoPermitidaError(f"La reserva {self._id_entidad} ya se encuentra confirmada.")
        self._estado = "CONFIRMADA"
        logger.registrar("INFO", f"Reserva {self._id_entidad} CONFIRMADA para {self._cliente.nombre}.")

    def cancelar(self):
        if self._estado == "CANCELADA":
            raise OperacionNoPermitidaError(f"La reserva {self._id_entidad} ya estaba cancelada.")
        self._estado = "CANCELADA"
        logger.registrar("INFO", f"Reserva {self._id_entidad} CANCELADA.")

    def obtener_resumen(self):
        return (f"Reserva [{self._id_entidad}] | Estado: {self._estado} | "
                f"Cliente: {self._cliente.nombre} | Servicio: {self._servicio.nombre} | "
                f"Duración: {self._duracion} | Total: ${self._costo_total:,.2f}")


# Desarrollo: parte 7: Gestor del Sistema Software FJ (Listas internas sin BD)

class SistemaSoftwareFJ:
    def __init__(self):
        # Toda la información se almacena en listas en memoria, sin bases de datos.
        self._clientes = []
        self._servicios = []
        self._reservas = []

    def registrar_cliente(self, id_cliente, nombre, documento, correo, telefono):
        try:
            nuevo_cliente = Cliente(id_cliente, nombre, documento, correo, telefono)
            self._clientes.append(nuevo_cliente)
        except ErrorSistemaFJ as e:
            logger.registrar("ERROR", f"Registro de cliente fallido ({id_cliente}): {e}")
            print(f"  [X] Error al registrar cliente: {e}")
            return None
        else:
            logger.registrar("INFO", f"Cliente registrado: {nuevo_cliente.obtener_resumen()}")
            print(f"  [OK] {nuevo_cliente.obtener_resumen()}")
            return nuevo_cliente

    def registrar_servicio(self, servicio_obj):
        try:
            if not isinstance(servicio_obj, Servicio):
                raise DatoInvalidoError("El objeto recibido no es un servicio válido.")
            self._servicios.append(servicio_obj)
        except ErrorSistemaFJ as e:
            logger.registrar("ERROR", f"Registro de servicio fallido: {e}")
            print(f"  [X] Error al registrar servicio: {e}")
            return None
        else:
            logger.registrar("INFO", f"Servicio registrado: {servicio_obj.describir_servicio()}")
            print(f"  [OK] {servicio_obj.describir_servicio()}")
            return servicio_obj

    def crear_y_procesar_reserva(self, id_reserva, cliente, servicio, duracion,
                                 descuento=0, impuesto=19, cargo_extra=0, confirmar=True):
        try:
            reserva = Reserva(id_reserva, cliente, servicio, duracion)
            reserva.procesar(descuento=descuento, impuesto=impuesto, cargo_extra=cargo_extra)
            if confirmar:
                reserva.confirmar()
            self._reservas.append(reserva)
        except ErrorSistemaFJ as e:
            # Si hubo encadenamiento de excepciones, mostramos también la causa original (__cause__).
            causa = f" (Causa: {e.__cause__})" if e.__cause__ else ""
            logger.registrar("ERROR", f"Fallo en reserva {id_reserva}: {e}{causa}")
            print(f"  [X] Error en reserva {id_reserva}: {e}{causa}")
            return None
        else:
            print(f"  [OK] {reserva.obtener_resumen()}")
            return reserva


# Desarrollo: parte 8: Simulación de 12 Operaciones Completas (Prueba Integral)

if __name__ == "__main__":
    print("=" * 75)
    print("   SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ (SIN BASE DE DATOS)")
    print("=" * 75)

    logger.registrar("EVENTO", "=== INICIO DE SIMULACIÓN DEL SISTEMA SOFTWARE FJ ===")
    sistema = SistemaSoftwareFJ()

    # --- OPERACIÓN 1: Registro válido de cliente ---
    print("\n1. Registrando Cliente válido (Ana Gómez):")
    c1 = sistema.registrar_cliente("CLI-01", "Ana Gómez", "10203040", "ana.gomez@correo.com", "3104567890")

    # --- OPERACIÓN 2: Registro válido de segundo cliente ---
    print("\n2. Registrando Cliente válido (Carlos Ruiz):")
    c2 = sistema.registrar_cliente("CLI-02", "Carlos Ruiz", "98765432", "carlos.ruiz@empresa.co", "3209876543")

    # --- OPERACIÓN 3: Registro inválido de cliente (correo mal formado) ---
    print("\n3. Intentando registrar Cliente con correo inválido:")
    sistema.registrar_cliente("CLI-03", "Pedro Pérez", "11223344", "pedro_sin_arroba.com", "3001112233")

    # --- OPERACIÓN 4: Registro inválido de cliente (parámetro faltante: nombre vacío) ---
    print("\n4. Intentando registrar Cliente con nombre vacío:")
    sistema.registrar_cliente("CLI-04", "", "55667788", "vacio@correo.com", "3004445566")

    # --- OPERACIÓN 5: Creación correcta de Servicio 1 (Reserva de Sala) ---
    print("\n5. Creando Servicio válido (Sala de Juntas):")
    s1 = None
    try:
        s1 = ReservaSala("SRV-01", "Sala Ejecutiva A", 80000, capacidad=12, incluye_proyector=True)
        sistema.registrar_servicio(s1)
    except ErrorSistemaFJ as e:
        logger.registrar("ERROR", f"Error creando servicio SRV-01: {e}")
        print(f"  [X] {e}")

    # --- OPERACIÓN 6: Creación correcta de Servicio 2 (Alquiler de Equipos) ---
    print("\n6. Creando Servicio válido (Alquiler de Portátiles):")
    s2 = None
    try:
        s2 = AlquilerEquipo("SRV-02", "Pack Portátiles Pro", 45000, "Laptop i7", cantidad_equipos=3)
        sistema.registrar_servicio(s2)
    except ErrorSistemaFJ as e:
        logger.registrar("ERROR", f"Error creando servicio SRV-02: {e}")
        print(f"  [X] {e}")

    # --- OPERACIÓN 7: Creación correcta de Servicio 3 (Asesoría Especializada) ---
    print("\n7. Creando Servicio válido (Asesoría en Ciberseguridad):")
    s3 = None
    try:
        s3 = AsesoriaEspecializada("SRV-03", "Auditoría Seguridad", 120000, "Ciberseguridad", modalidad="Presencial")
        sistema.registrar_servicio(s3)
    except ErrorSistemaFJ as e:
        logger.registrar("ERROR", f"Error creando servicio SRV-03: {e}")
        print(f"  [X] {e}")

    # --- OPERACIÓN 8: Creación incorrecta de Servicio (tarifa negativa) ---
    print("\n8. Intentando crear Servicio con tarifa negativa:")
    try:
        s_invalido = ReservaSala("SRV-04", "Sala Errónea", -50000, capacidad=5)
        sistema.registrar_servicio(s_invalido)
    except ErrorSistemaFJ as e:
        logger.registrar("ERROR", f"Creación de servicio fallida (SRV-04): {e}")
        print(f"  [X] Error al crear servicio: {e}")

    # --- OPERACIÓN 9: Reserva exitosa (uso de sobrecarga con parámetros básicos) ---
    print("\n9. Creando Reserva exitosa (Sala Ejecutiva por 3 horas, sin descuento, IVA 19%):")
    r1 = sistema.crear_y_procesar_reserva("RES-01", c1, s1, duracion=3)

    # --- OPERACIÓN 10: Reserva exitosa (sobrecarga con descuento + impuesto) y posterior cancelación ---
    print("\n10. Creando Reserva exitosa (Alquiler Equipos por 2 días, 10% descuento) y cancelándola:")
    r2 = sistema.crear_y_procesar_reserva("RES-02", c2, s2, duracion=2, descuento=10, impuesto=19)
    if r2:
        r2.cancelar()
        print(f"  [OK] Nuevo estado: {r2.obtener_resumen()}")

    # --- OPERACIÓN 11: Reserva fallida (Servicio marcado como no disponible) ---
    print("\n11. Intentando reservar un servicio NO disponible:")
    if s3:
        s3.disponible = False
        sistema.crear_y_procesar_reserva("RES-03", c1, s3, duracion=2)

    # --- OPERACIÓN 12: Reserva fallida por cálculo inconsistente + operación no permitida ---
    print("\n12. Probando cálculo inconsistente (descuento 150%) y operación no permitida (confirmar cancelada):")
    sistema.crear_y_procesar_reserva("RES-04", c2, s1, duracion=2, descuento=150)

    try:
        if r2:
            r2.confirmar()  # r2 fue cancelada en la operación 10, debe lanzar OperacionNoPermitidaError
    except OperacionNoPermitidaError as e:
        logger.registrar("ERROR", f"Operación no permitida detectada: {e}")
        print(f"  [X] Operación bloqueada correctamente: {e}")

    logger.registrar("EVENTO", "=== FIN DE SIMULACIÓN DEL SISTEMA SOFTWARE FJ ===")
    print("\n" + "=" * 75)
    print("Simulación finalizada sin interrupciones. Revisa el archivo 'logs_software_fj.txt'.")
    print("=" * 75)
