import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
import ctypes
import os
import logging
import time

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Estructura para información del dispositivo
class SGDeviceInfoParam(ctypes.Structure):
    _fields_ = [
        ("DeviceID", ctypes.c_ulong),
        ("DeviceSN", ctypes.c_char * 16),
        ("ComPort", ctypes.c_ulong),
        ("ComSpeed", ctypes.c_ulong),
        ("ImageWidth", ctypes.c_ulong),
        ("ImageHeight", ctypes.c_ulong),
        ("Contrast", ctypes.c_ulong),
        ("Brightness", ctypes.c_ulong),
        ("Gain", ctypes.c_ulong),
        ("ImageDPI", ctypes.c_ulong),
        ("FWVersion", ctypes.c_ulong)
    ]

# Estructura para información de la huella
class SGFingerInfo(ctypes.Structure):
    _fields_ = [
        ("FingerNumber", ctypes.c_ushort),
        ("ViewNumber", ctypes.c_ushort),
        ("ImpressionType", ctypes.c_ushort),
        ("ImageQuality", ctypes.c_ushort)
    ]

# Configuración global del SDK
SGFPM = None
hFPM = None
DLL_PATH = r'C:\Users\facil\Desktop\ADWEB-main\bin'

def load_dll():
    global SGFPM
    try:
        # Asegurar que el directorio bin esté en el PATH
        os.environ['PATH'] = DLL_PATH + os.pathsep + os.environ['PATH']
        dll_path = os.path.join(DLL_PATH, 'sgfplib.dll')
        logger.info(f"Intentando cargar DLL desde: {dll_path}")
        SGFPM = ctypes.CDLL(dll_path)
        logger.info("DLL cargada correctamente")

        # Declarar funciones clave
        SGFPM.SGFPM_Create.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        SGFPM.SGFPM_Create.restype = ctypes.c_long

        SGFPM.SGFPM_Init.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        SGFPM.SGFPM_Init.restype = ctypes.c_long

        SGFPM.SGFPM_OpenDevice.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        SGFPM.SGFPM_OpenDevice.restype = ctypes.c_long

        SGFPM.SGFPM_GetDeviceInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(SGDeviceInfoParam)]
        SGFPM.SGFPM_GetDeviceInfo.restype = ctypes.c_long

        SGFPM.SGFPM_GetImageEx.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_ulong,
            ctypes.c_void_p,
            ctypes.c_ulong
        ]
        SGFPM.SGFPM_GetImageEx.restype = ctypes.c_long

        SGFPM.SGFPM_GetMaxTemplateSize.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
        SGFPM.SGFPM_GetMaxTemplateSize.restype = ctypes.c_long

        SGFPM.SGFPM_CreateTemplate.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(SGFingerInfo),
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte)
        ]
        SGFPM.SGFPM_CreateTemplate.restype = ctypes.c_long

        SGFPM.SGFPM_MatchTemplate.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_ulong,
            ctypes.POINTER(ctypes.c_bool)
        ]
        SGFPM.SGFPM_MatchTemplate.restype = ctypes.c_long

        SGFPM.SGFPM_CloseDevice.argtypes = [ctypes.c_void_p]
        SGFPM.SGFPM_CloseDevice.restype = ctypes.c_long

        SGFPM.SGFPM_Terminate.argtypes = [ctypes.c_void_p]
        SGFPM.SGFPM_Terminate.restype = ctypes.c_long

    except Exception as e:
        logger.error(f"Error cargando DLL: {str(e)}")
        raise

def init_sdk():
    global hFPM
    try:
        if SGFPM is None:
            load_dll()

        hFPM = ctypes.c_void_p()
        logger.info("Llamando a SGFPM_Create...")
        result = SGFPM.SGFPM_Create(ctypes.byref(hFPM))
        if result != 0:
            logger.error(f"SGFPM_Create falló con código de error: {result}")
            return None
        logger.info(f"SGFPM_Create exitoso. Manejador: {hFPM.value}")

        logger.info("Llamando a SGFPM_Init con device_type=6...")
        result = SGFPM.SGFPM_Init(hFPM, 6)  # SG_DEV_FDU05 para HU20
        if result != 0:
            logger.error(f"SGFPM_Init falló con código de error: {result}")
            SGFPM.SGFPM_Terminate(hFPM)
            return None
        logger.info("SGFPM_Init exitoso")

        logger.info("Llamando a SGFPM_OpenDevice...")
        result = SGFPM.SGFPM_OpenDevice(hFPM, 0)  # USB_AUTO_DETECT
        if result != 0:
            logger.error(f"SGFPM_OpenDevice falló con código de error: {result}")
            SGFPM.SGFPM_Terminate(hFPM)
            return None
        logger.info("SGFPM_OpenDevice exitoso")

        logger.info("Dispositivo inicializado correctamente")
        return hFPM
    except Exception as e:
        logger.error(f"Excepción en init_sdk: {str(e)}")
        return None

def close_sdk(hFPM):
    if hFPM and SGFPM:
        result = SGFPM.SGFPM_CloseDevice(hFPM)
        if result != 0:
            logger.error(f"Error al cerrar el dispositivo: {result}")
        else:
            logger.info("Dispositivo cerrado correctamente")
        
        result = SGFPM.SGFPM_Terminate(hFPM)
        if result != 0:
            logger.error(f"Error al terminar el SDK: {result}")
        else:
            logger.info("SDK terminado correctamente")

@app.route('/init', methods=['POST'])
def initialize_device():
    global hFPM
    hFPM = init_sdk()
    if hFPM:
        return jsonify({'status': 'ready'})
    return jsonify({'status': 'error', 'error': 'Initialization failed'}), 500

@app.route('/capture', methods=['POST'])
def capture():
    global hFPM
    if hFPM is None:
        hFPM = init_sdk()
        if hFPM is None:
            return jsonify({'error': 'Device initialization failed'}), 500
    
    try:
        logger.info("Iniciando captura de huella...")

        # Obtener información del dispositivo
        device_info = SGDeviceInfoParam()
        logger.info("Obteniendo información del dispositivo...")
        result = SGFPM.SGFPM_GetDeviceInfo(hFPM, ctypes.byref(device_info))
        if result != 0:
            logger.error(f"Error en GetDeviceInfo: {result}")
            raise Exception(f"Error en GetDeviceInfo: {result}")
        logger.info(f"Dimensiones de la imagen: {device_info.ImageWidth}x{device_info.ImageHeight}")

        # Capturar la imagen
        width, height = device_info.ImageWidth, device_info.ImageHeight
        image_buffer = (ctypes.c_ubyte * (width * height))()
        logger.info("Esperando huella... Coloque el dedo en el sensor.")
        timeout_ms = 10000
        quality_threshold = 50
        result = SGFPM.SGFPM_GetImageEx(hFPM, image_buffer, timeout_ms, None, quality_threshold)
        if result != 0:
            error_msg = {
                54: "Timeout: No se detectó huella",
                57: "Imagen no válida",
                58: "Falta de ancho de banda USB"
            }.get(result, f"Error desconocido: {result}")
            logger.error(f"Error en GetImageEx: {error_msg}")
            raise Exception(f"Error en GetImageEx: {error_msg}")
        logger.info("Imagen capturada correctamente")

        # Obtener tamaño máximo del template
        max_template_size = ctypes.c_ulong()
        result = SGFPM.SGFPM_GetMaxTemplateSize(hFPM, ctypes.byref(max_template_size))
        if result != 0:
            logger.error(f"Error en GetMaxTemplateSize: {result}")
            raise Exception(f"Error en GetMaxTemplateSize: {result}")
        logger.info(f"Tamaño máximo del template: {max_template_size.value}")

        # Crear el template
        template_buffer = (ctypes.c_ubyte * max_template_size.value)()
        finger_info = SGFingerInfo(FingerNumber=0, ViewNumber=0, ImpressionType=0, ImageQuality=quality_threshold)
        result = SGFPM.SGFPM_CreateTemplate(hFPM, ctypes.byref(finger_info), image_buffer, template_buffer)
        if result != 0:
            logger.error(f"Error en CreateTemplate: {result}")
            raise Exception(f"Error en CreateTemplate: {result}")
        logger.info("Template creado correctamente")

        # Convertir a base64
        template_data = bytes(template_buffer)
        return jsonify({'template': base64.b64encode(template_data).decode('utf-8')})

    except Exception as e:
        logger.error(f"Error en capture: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        close_sdk(hFPM)
        hFPM = None

@app.route('/match', methods=['POST'])
def match():
    global hFPM
    if hFPM is None:
        hFPM = init_sdk()
        if hFPM is None:
            return jsonify({'error': 'No se pudo inicializar el dispositivo'}), 500
    
    try:
        # Obtener los templates desde la solicitud
        data = request.get_json()
        template1_b64 = data['template1']
        template2_b64 = data['template2']

        # Decodificar los templates desde base64
        template1 = base64.b64decode(template1_b64)
        template2 = base64.b64decode(template2_b64)

        # Verificar que los templates no estén vacíos
        logger.info(f"Tamaño de template1: {len(template1)} bytes")
        logger.info(f"Tamaño de template2: {len(template2)} bytes")
        if len(template1) == 0 or len(template2) == 0:
            raise ValueError("Uno o ambos templates están vacíos")

        # Convertir los templates a buffers compatibles con el SDK
        template1_buffer = (ctypes.c_ubyte * len(template1)).from_buffer_copy(template1)
        template2_buffer = (ctypes.c_ubyte * len(template2)).from_buffer_copy(template2)

        # Realizar la coincidencia
        matched = ctypes.c_bool()
        result = SGFPM.SGFPM_MatchTemplate(hFPM, template1_buffer, template2_buffer, 5, ctypes.byref(matched))
        if result != 0:
            logger.error(f"Error en MatchTemplate: {result}")
            raise Exception(f"Error en MatchTemplate: {result}")

        # Devolver el resultado
        score = 100 if matched.value else 0
        logger.info(f"Coincidencia: {'Sí' if matched.value else 'No'}")
        return jsonify({'score': score})
    except Exception as e:
        logger.error(f"Error en match: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/shutdown', methods=['POST'])
def shutdown():
    global hFPM
    try:
        if hFPM and SGFPM:
            close_sdk(hFPM)
            hFPM = None
        return jsonify({'status': 'shutdown'})
    except Exception as e:
        logger.error(f"Error al cerrar: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=9000)
    except Exception as e:
        logger.error(f"Error al iniciar el servidor: {str(e)}")
    finally:
        if hFPM and SGFPM:
            close_sdk(hFPM)