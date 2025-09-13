# controllers/my_controller/my_controller.py
from controller import Robot
import os, csv

print("[my_controller] started")

robot = Robot()
TIME_STEP = int(robot.getBasicTimeStep()) or 32

# --- Utilidad para encontrar devices por nombre ---
def get_first_device(names):
    for n in names:
        try:
            d = robot.getDevice(n)
            if d is not None:
                return d
        except Exception:
            pass
    return None

# Motores (ajusta los nombres si difieren en tu mundo)
left  = get_first_device(['left wheel motor', 'left motor', 'left_wheel'])
right = get_first_device(['right wheel motor', 'right motor', 'right_wheel'])
for m in (left, right):
    assert m is not None, "No encontré los motores: revisa los nombres en la Scene Tree."
    m.setPosition(float('inf'))  # modo velocidad
    m.setVelocity(0.0)

# LiDAR (nombres típicos en TB3/Webots)
lidar = get_first_device(['Lidar', 'Hokuyo', 'LDS-01', 'RPLIDAR'])
assert lidar is not None, "No encontré un LiDAR: verifica el nombre en la Scene Tree."
lidar.enable(TIME_STEP)

# Info del LiDAR
res = int(lidar.getHorizontalResolution())
fov = lidar.getFov()  # radianes (no usado, pero útil tenerlo)

# -------- Logging CSV (ubicado junto al controlador para webots.cloud) --------
# Guardamos en el mismo directorio del script para que sea fácil descargarlo.
here = os.path.dirname(__file__)
log_path = os.path.join(here, 'lidar_log.csv')

csv_file = open(log_path, 'w', newline='')
writer = csv.writer(csv_file)
writer.writerow(['sim_time'] + [f'r{i}' for i in range(res)])
csv_file.flush()
print(f"[INFO] Guardando scans en: {log_path}")

# Movimiento simple: avanza y gira
fwd  = 3.0   # rad/s por rueda
turn = 2.0   # rad/s (giro en sitio)
state, ticks = 'forward', 0

try:
    while robot.step(TIME_STEP) != -1:
        # Lee LiDAR
        ranges = list(lidar.getRangeImage())  # lista de distancias (m)
        sim_time = robot.getTime()
        writer.writerow([sim_time] + ranges)
        csv_file.flush()

        # Control de motores
        if state == 'forward':
            left.setVelocity(fwd); right.setVelocity(fwd)
            ticks += 1
            if ticks > 80:
                state, ticks = 'turn', 0
        else:  # 'turn'
            left.setVelocity(turn); right.setVelocity(-turn)
            ticks += 1
            if ticks > 40:
                state, ticks = 'forward', 0
finally:
    try:
        csv_file.close()
    except Exception:
        pass
