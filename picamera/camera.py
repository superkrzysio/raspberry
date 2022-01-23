import time

class PiCamera:
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def capture_continuous(self, s, burst=False):
        print("[PICAMERA STUB] Capturing...")
        capture_time = 1
        if burst:
            capture_time = 0.5
        time.sleep(capture_time)
        return range(0, 10000)
