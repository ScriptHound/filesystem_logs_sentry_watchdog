import time
import sentry_sdk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(".env")
# Initialize Sentry SDK with your DSN
sentry_sdk.init(os.getenv("SENTRY_DSN"))

class NewLogFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        # This function is called when a new file is created in the monitored directory
        if not event.is_directory:
            file_path = Path(event.src_path)
            print(f"New file created: {file_path}")  # Logging for demonstration
            try:
                with open(file_path, 'r') as file:
                    log_content = file.read()
                    # Here you could parse the log content or extract specific information
                    sentry_sdk.capture_message(f"New log file created: {file_path}\nContent:\n{log_content}")
            except Exception as e:
                print(f"Failed to read or send log file {file_path} to Sentry: {e}")

def start_monitoring(directory):
    event_handler = NewLogFileHandler()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    print(f"Monitoring started on directory: {directory}")
    try:
        while True:
            time.sleep(10)  # Keep the script running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    logs_directory = "configure it"
    start_monitoring(logs_directory)
