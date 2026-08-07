"""YOLO inference and safe webcam lifecycle helpers."""

from __future__ import annotations

import threading
import time
from collections.abc import Generator
from pathlib import Path

import cv2
from ultralytics import YOLO


PROJECT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_DIR / "yolo11l.pt"
model = YOLO(str(MODEL_PATH))

camera: cv2.VideoCapture | None = None
live_counts: dict[str, int] = {}
camera_lock = threading.RLock()


def detect_image(image_path: str):
    """Detect every supported YOLO class in an uploaded image."""
    output_folder = PROJECT_DIR / "static" / "output"
    output_folder.mkdir(parents=True, exist_ok=True)
    results = model.predict(
        source=image_path,
        conf=0.55,
        iou=0.45,
        imgsz=960,
        max_det=1000,
        augment=False,
        save=False,
        verbose=False,
    )
    results[0].save(filename=str(output_folder / "result.jpg"))
    return results


def _open_camera() -> cv2.VideoCapture:
    """Open the physical webcam only when the stream endpoint is requested."""
    global camera
    with camera_lock:
        if camera is not None and camera.isOpened():
            return camera
        if camera is not None:
            camera.release()
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            camera.release()
            camera = None
            raise RuntimeError("Unable to open camera. Check that it is connected and not in use.")
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return camera

def generate_frames() -> Generator[bytes, None, None]:
    """Generate MJPEG frames from webcam."""
    global live_counts

    active_camera = _open_camera()
    previous_time = time.time()

    try:
        while True:

            # Read frame
            with camera_lock:
                if camera is not active_camera or not active_camera.isOpened():
                    break

                success, frame = active_camera.read()

            print("Camera Read:", success)

            if not success:
                print("Camera read failed")
                break

            # YOLO Detection
            results = model.predict(
                source=frame,
                conf=0.55,
                iou=0.45,
                imgsz=640,
                max_det=1000,
                verbose=False
            )

            result = results[0]
            annotated = result.plot()

            frame_counts = {}

            for box in result.boxes:
                cls = int(box.cls[0])
                label = result.names[cls]
                frame_counts[label] = frame_counts.get(label, 0) + 1

            with camera_lock:
                if camera is not active_camera:
                    break

                live_counts = frame_counts

            # Draw object counts
            y = 35

            for label, count in frame_counts.items():
                cv2.putText(
                    annotated,
                    f"{label}: {count}",
                    (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75,
                    (0, 255, 0),
                    2
                )
                y += 30

            cv2.putText(
                annotated,
                f"Total Objects: {sum(frame_counts.values())}",
                (10, y + 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

            # FPS
            current_time = time.time()
            fps = 1 / max(current_time - previous_time, 0.001)
            previous_time = current_time

            cv2.putText(
                annotated,
                f"FPS: {int(fps)}",
                (10, annotated.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )

            cv2.putText(
                annotated,
                "YOLO11L AI RUNNING",
                (annotated.shape[1] - 280, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            # Encode JPEG
            ok, buffer = cv2.imencode(".jpg", annotated)

            print("JPEG Encode:", ok)

            if not ok:
                continue

            frame_bytes = buffer.tobytes()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + frame_bytes +
                b"\r\n"
            )

    finally:
        with camera_lock:
            if camera is active_camera:
                active_camera.release()
                globals()["camera"] = None
                live_counts = {}


def get_live_counts() -> dict[str, int]:
    with camera_lock:
        return live_counts.copy()


def release_camera() -> bool:
    """Release the webcam safely; repeated Stop requests are harmless."""
    global camera, live_counts
    with camera_lock:
        was_running = camera is not None
        if camera is not None:
            camera.release()
            camera = None
        live_counts = {}
    try:
        cv2.destroyAllWindows()
    except cv2.error:
        pass
    return was_running
