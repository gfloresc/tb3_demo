# controllers/my_controller/my_controller.py
from controller import Robot
import os, csv, math

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
right = get_first_device(['right wheel motor','right motor','right_wheel'])
for m in (left, right):
    assert m is not None, "No encontré los motores: revisa los nombres en la Scene Tree."
    m.setPosition(float('inf'))
    m.setVelocity(0.0)

# LiDAR (nombres típicos en TB3/Webots)
lidar = get_first_device(['Lidar', 'Hokuyo', 'LDS-01', 'RPLIDAR'])
assert lidar is not None, "No encontré un LiDAR: verifica el nombre en la Scene Tree."
lidar.enable(TIME_STEP)

# Info del LiDAR
res = lidar.getHorizontalResolution()
fov = lidar.getFov()  # radianes

# Archivo de log (para graficar luego)
log_dir = os.path.expanduser('~/webots_logs')
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'lidar_log.csv')

# Prepara CSV: primera fila = encabezado
new_file = not os.path.exists(log_path)
csv_file = open(log_path, 'w', newline='')
writer = csv.writer(csv_file)
writer.writerow(['sim_time'] + [f'r{i}' for i in range(res)])
csv_file.flush()
print(f"[INFO] Guardando scans en: {log_path}")

# Movimiento simple: avanza y gira
fwd  = 3.0    # rad/s
turn = 2.0
state, ticks = 'forward', 0

while robot.step(TIME_STEP) != -1:
    # Lee LiDAR
    ranges = list(lidar.getRangeImage())  # lista de distancias (m)
    sim_time = robot.getTime()
    writer.writerow([sim_time] + ranges)
    csv_file.flush()

    # Mueve el robot
    if state == 'forward':
        left.setVelocity(fwd); right.setVelocity(fwd)
        ticks += 1
        if ticks > 80:
            state, ticks = 'turn', 0
    elif state == 'turn':
        left.setVelocity(turn); right.setVelocity(-turn)
        ticks += 1
        if ticks > 40:
            state, ticks = 'forward', 0
