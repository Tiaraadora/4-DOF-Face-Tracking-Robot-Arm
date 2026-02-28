import cv2
import serial
import time
import threading


# Fungsi thread untuk baca respon dari Arduino
def read_from_arduino(arduino):
    while True:
        try:
            line = arduino.readline().decode(errors='ignore').strip()
            if line:
                print(f"Arduino says: {line}")
        except:
            break


# Hubungkan ke Arduino
arduino = serial.Serial('COM4', 9600, timeout=1)
time.sleep(2)

# Buka kamera
cap = cv2.VideoCapture(0)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# frame_width = int(cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720))
# frame_height = int(cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480))
print(frame_width)
print(frame_height)

# Load Haar Cascade untuk deteksi wajah
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

prev_x = 90  # posisi awal servo
hysteresis_counter = 0  # Counter for hysteresis
last_raw_x = 90

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)  # biar gak mirror
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)  # Back to 5 for sensitivity

    if len(faces) > 0:
        # Ambil wajah terbesar
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        (x, y, w, h) = faces[0]

        # Gambar kotak hijau di wajah
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Hitung titik tengah wajah (untuk servo X)
        center_x = x + w // 2
        print(f"center_x: {center_x}")

        titik_tengah = frame_width/2
        mapped_x= center_x - titik_tengah
        print(mapped_x," ",center_x,end= " ")
        mapped_x = int((mapped_x / titik_tengah) * 30)
        print(mapped_x,end= " ")

        # Hitung area (untuk servo Y)
        area = w * h
        area = min(area, 50000)

        # Buat data string "x,area"
        data = f"{mapped_x},{area}\n"
        print(f"Sending to Arduino: {data.strip()}")

        # Kirim data ke Arduino
        arduino.write(data.encode())

        # Info di layar
        text = f"X:{mapped_x} Area:{area}"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 0, 255), 2)
    else:
        # No face → Reset to neutral
        data = "0,25000\n"
        print("No face detected → Sending reset: 90,25000")
        arduino.write(data.encode())
        prev_x = 90
        hysteresis_counter = 0
        last_raw_x = 90

    # Tampilkan frame
    cv2.imshow('Face Tracking', frame)

    # Tekan 'q' untuk keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Bersihkan
cap.release()
cv2.destroyAllWindows()
arduino.close()