from flask import Flask, request, jsonify
from flask_cors import CORS
import ctypes
import os
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# 1. Configuración Correcta del SDK para HU20 (USB)
# ------------------------------------------------------------
class SGDeviceInfoParam(ctypes.Structure):
    _fields_ = [
        ("DeviceID", ctypes.c_ulong),
        ("DeviceSN", ctypes.c_char * 16),
        ("ComPort", ctypes.c_ulong),
        ("ImageWidth", ctypes.c_ulong),
        ("ImageHeight", ctypes.c_ulong),
        ("Contrast", ctypes.c_ulong),
        ("Brightness", ctypes.c_ulong),
        ("Gain", ctypes.c_ulong),
        ("ImageDPI", ctypes.c_ulong),
        ("FWVersion", ctypes.c_ulong)
    ]

# ------------------------------------------------------------
# 2. Declaraciones de Funciones Correctas (Revisadas del Manual)
# ------------------------------------------------------------
SGFPM = None
device_handle = ctypes.c_void_p()

def load_dll():
    global SGFPM
    try:
        dll_path = os.path.join(os.path.dirname(__file__), 'bin', 'sgfplib.dll')
        SGFPM = ctypes.WinDLL(dll_path)
        
        # Declaraciones exactas según SDK
        SGFPM.SGFPM_Create.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        SGFPM.SGFPM_Create.restype = ctypes.c_long
        
        SGFPM.SGFPM_Init.argtypes = [ctypes.c_void_p, ctypes.c_ulong]  # ¡Clave!
        SGFPM.SGFPM_Init.restype = ctypes.c_long
        
        SGFPM.SGFPM_OpenDevice.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        SGFPM.SGFPM_OpenDevice.restype = ctypes.c_long
        
        SGFPM.SGFPM_GetDeviceInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(SGDeviceInfoParam)]
        SGFPM.SGFPM_GetDeviceInfo.restype = ctypes.c_long
        
        SGFPM.SGFPM_GetImage.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_ulong,
            ctypes.c_ulong,
            ctypes.c_ulong
        ]
        SGFPM.SGFPM_GetImage.restype = ctypes.c_long
        
    except Exception as e:
        logger.error(f"Error cargando DLL: {str(e)}")
        raise

# ------------------------------------------------------------
# 3. Inicialización Correcta para HU20 (SG_DEV_FDU05 = 0x06)
# ------------------------------------------------------------
def init_sdk():
    global device_handle
    try:
        load_dll()
        
     # 1. Inicializar para HU20 (SG_DEV_FDU05 = 6)
        result = SGFPM.SGFPM_Init(device_handle, 6)  # ¡Valor crítico!
        if result != 0:
            raise Exception(f"SGFPM_Init Error {result}: Verifique sgfdusd*.dll")

        # 2. Abrir dispositivo con AUTO_DETECT (0)
        result = SGFPM.SGFPM_OpenDevice(device_handle, 0)
        if result != 0:
            raise Exception(f"OpenDevice Error: {result} (¿HU20 conectado?)")

        # 3. Obtener información del dispositivo para dimensiones
        device_info = SGDeviceInfoParam()
        result = SGFPM.SGFPM_GetDeviceInfo(device_handle, ctypes.byref(device_info))
        if result != 0:
            raise Exception(f"GetDeviceInfo Error: {result}")

        logger.info("Dispositivo inicializado correctamente")
        
    except Exception as e:
        logger.error(f"Error SDK: {str(e)}")
        raise

# ------------------------------------------------------------
# 4. Endpoints Flask
# ------------------------------------------------------------
@app.route('/init', methods=['POST'])
def initialize_device():
    try:
        init_sdk()
        return jsonify({'status': 'ready', 'message': 'HU20 inicializado'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/capture', methods=['POST'])
def capture():
    try:
        # Obtener información del dispositivo
        device_info = SGDeviceInfoParam()
        result = SGFPM.SGFPM_GetDeviceInfo(device_handle, ctypes.byref(device_info))
        if result != 0:
            return jsonify({'error': f"GetDeviceInfo Error: {result}"}), 500
            
     # 1. Obtener dimensiones desde device_info
        width = device_info.ImageWidth  # Ej: 300
        height = device_info.ImageHeight  # Ej: 400
        buffer_size = width * height

        # 2. Inicializar buffer
        image_buffer = (ctypes.c_ubyte * buffer_size)()

        # 3. Capturar imagen
        result = SGFPM.SGFPM_GetImage(
            device_handle,
            image_buffer,
            width,
            height,
            0  # Timeout (0 = infinito)
        )
        
        if result != 0:
            # Errores comunes del SDK (ver Capítulo 6.7 del manual)
            error_msg = {
                57: "ERROR_WRONG_IMAGE: No se detectó huella",
                53: "ERROR_LINE_DROPPED: Fallo de comunicación USB",
                54: "ERROR_TIME_OUT: Tiempo de espera agotado"
            }.get(result, f"Código de error desconocido: {result}")
            return jsonify({'error': error_msg}), 500

        # 4. Convertir imagen a base64 (opcional)
        import base64
        image_base64 = base64.b64encode(bytes(image_buffer)).decode('utf-8')
        
        return jsonify({
            'width': width,
            'height': height,
            'image': image_base64
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# ------------------------------------------------------------
# 5. Requerimientos Clave para Ejecución
# ------------------------------------------------------------
"""
- Copiar estos DLLs a /bin/:
   sgfplib.dll, sgfpamx.dll, sgfdusdax64.dll (¡No necesario para USB!), sgfdu05.dll (HU20)
- Ejecutar como Administrador
- Conectar HU20 directamente al puerto USB
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)