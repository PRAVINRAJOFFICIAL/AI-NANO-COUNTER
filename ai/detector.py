from ultralytics import YOLO
import cv2
import os
import time

# ==========================================
# Load YOLO11 Large Model
# ==========================================
model = YOLO("yolo11l.pt")

# Global Variables
camera = None
live_counts = {}


# ==========================================
# Image Detection
# ==========================================
def detect_image(image_path):

    output_folder = "static/output"
    os.makedirs(output_folder, exist_ok=True)

    results = model.predict(
        source=image_path,
        conf=0.55,
        iou=0.45,
        imgsz=960,
        max_det=100,
        augment=False,
        save=False,
        verbose=False
    )

    output_path = os.path.join(output_folder, "result.jpg")
    results[0].save(filename=output_path)

    return results


# ==========================================
# Live Camera Detection
# ==========================================
def generate_frames():

    global camera
    global live_counts

    if camera is None:

        camera = cv2.VideoCapture(0)

        if not camera.isOpened():
            raise RuntimeError("Unable to open camera")

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    prev_time = time.time()

    while True:

        success, frame = camera.read()

        if not success:
            break

        # YOLO Detection
        results = model.predict(
            source=frame,
            conf=0.55,
            iou=0.45,
            imgsz=640,
            verbose=False
        )

        annotated = results[0].plot()

        names = results[0].names

        counts = {}

        # Object Count
        for box in results[0].boxes:

            cls = int(box.cls[0])

            label = names[cls]

            counts[label] = counts.get(label, 0) + 1

        # Save Counts
        live_counts = counts.copy()

        # Draw Count
        y = 35

        total = 0

        for key, value in counts.items():

            total += value

            cv2.putText(
                annotated,
                f"{key}: {value}",
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (0, 255, 0),
                2
            )

            y += 30

        # Total Objects
        cv2.putText(
            annotated,
            f"Total Objects : {total}",
            (10, y + 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        # FPS
        current_time = time.time()

        fps = 1 / (current_time - prev_time)

        prev_time = current_time

        cv2.putText(
            annotated,
            f"FPS : {int(fps)}",
            (10, annotated.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2
        )

        # AI Status
        cv2.putText(
            annotated,
            "YOLO11L AI RUNNING",
            (annotated.shape[1] - 260, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        # Convert Frame
        ret, buffer = cv2.imencode(".jpg", annotated)

        if not ret:
            continue

        frame = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            + frame +
            b'\r\n'
        )


# ==========================================
# Return Live Counts
# ==========================================
def get_live_counts():

    return live_counts


# ==========================================
# Release Camera
# ==========================================
def release_camera():

    global camera

    if camera is not None:

        camera.release()

        camera = None

        cv2.destroyAllWindows()