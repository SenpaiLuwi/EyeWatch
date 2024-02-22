import cv2
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from datetime import datetime
import getpass
import os
import json


class FaceCaptureApp:
    CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "EyeWatch_File", "EyeWatch_config.json")

    def __init__(self, root):
        self.root = root
        self.root.title("EyeWatch | Luwi, Migs, Rots")

        self.cap = None
        self.active_camera = 0
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        self.camera_names = self.detect_cameras()
        self.selected_camera = tk.StringVar(value=self.camera_names[0] if self.camera_names else "")

        self.user_info = {}

        self.home_frame = ttk.Frame(self.root)

        self.current_frame = None

        self.image_location_entry = ttk.Entry(self.home_frame, state="readonly", textvariable=tk.StringVar(value=""))

        self.create_home_widgets()

        self.show_frame(self.home_frame)

        self.create_configuration_file()
        self.load_configuration()

    def create_home_widgets(self):
        self.camera_dropdown = ttk.Combobox(self.home_frame, textvariable=self.selected_camera, values=self.camera_names)
        self.camera_dropdown.grid(row=1, column=0, pady=10, padx=10)

        self.active_camera_button = ttk.Button(self.home_frame, text="Active Camera", command=self.start_capture)
        self.active_camera_button.grid(row=2, column=0, pady=10, padx=10)

        self.stop_capture_button = ttk.Button(self.home_frame, text="Stop Capture", command=self.stop_capture_function)
        self.stop_capture_button.grid(row=3, column=0, pady=10, padx=10)

        self.home_button = ttk.Button(self.home_frame, text="Home", command=self.stop_capture_function)
        self.home_button.grid(row=0, column=1, pady=10, padx=10)

        self.tools_button = ttk.Button(self.home_frame, text="Tools", command=self.stop_capture_function)
        self.tools_button.grid(row=0, column=3, pady=10, padx=10)

        self.save_image_location_button = ttk.Button(self.home_frame, text="Save Image Location", command=self.set_image_location)
        self.save_image_location_button.grid(row=4, column=0, pady=10, padx=10)

        self.save_video_location_button = ttk.Button(self.home_frame, text="Save Video Location", command=self.set_video_location)
        self.save_video_location_button.grid(row=6, column=0, pady=10, padx=10)

        self.image_location_label = ttk.Label(self.home_frame, text="Image Save Location:")
        self.image_location_entry = ttk.Entry(self.home_frame, state="readonly", textvariable=tk.StringVar(value=""))
        self.image_location_label.grid(row=5, column=0, pady=10, padx=10, sticky="e")
        self.image_location_entry.grid(row=5, column=1, pady=10, padx=10, sticky="w")

        self.video_location_label = ttk.Label(self.home_frame, text="Video Save Location:")
        self.video_location_entry = ttk.Entry(self.home_frame, state="readonly", textvariable=tk.StringVar(value=""))
        self.video_location_label.grid(row=7, column=0, pady=10, padx=10, sticky="e")
        self.video_location_entry.grid(row=7, column=1, pady=10, padx=10, sticky="w")

        self.camera_canvas = tk.Canvas(self.home_frame, width=700, height=500)
        self.camera_canvas.grid(row=1, column=1, rowspan=3, columnspan=3, padx=50, pady=50)

    def create_configuration_file(self):
        config_file_path = self.CONFIG_FILE_PATH.format(username=getpass.getuser())
        config_dir = os.path.dirname(config_file_path)

        os.makedirs(config_dir, exist_ok=True)

        if not os.path.exists(config_file_path):
            with open(config_file_path, 'w') as file:
                json.dump({}, file)

    def load_configuration(self):
        try:
            with open(self.CONFIG_FILE_PATH.format(username=getpass.getuser()), 'r') as file:
                config_data = json.load(file)

            self.image_location_entry.config(state=tk.NORMAL)
            self.image_location_entry.delete(0, tk.END)
            self.image_location_entry.insert(0, config_data.get("image_location", ""))
            self.image_location_entry.config(state="readonly")

        except FileNotFoundError:
            self.create_configuration_file()

    def save_configuration(self):
        config_data = {"image_location": self.image_location_entry.get()}

        with open(self.CONFIG_FILE_PATH.format(username=getpass.getuser()), 'w') as file:
            json.dump(config_data, file)

    def set_image_location(self):
        location = tk.filedialog.askdirectory()
        self.image_location_entry.config(state=tk.NORMAL)
        self.image_location_entry.delete(0, tk.END)
        self.image_location_entry.insert(0, location)
        self.image_location_entry.config(state="readonly")
        self.save_configuration()

    def set_video_location(self):
        location = tk.filedialog.askdirectory()
        self.video_location_entry.config(state=tk.NORMAL)
        self.video_location_entry.delete(0, tk.END)
        self.video_location_entry.insert(0, location)
        self.video_location_entry.config(state="readonly")

    def show_frame(self, frame):
        if self.current_frame:
            self.current_frame.grid_forget()
        frame.grid(row=0, column=0, sticky="nsew")
        self.current_frame = frame

    def detect_cameras(self):
        camera_list = []
        for i in range(5):  # aayusin pa
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    camera_list.append(f"Camera {i}")
                cap.release()
        return camera_list

    def start_capture(self):
        selected_camera_index = int(self.selected_camera.get().split()[-1])
        self.cap = cv2.VideoCapture(selected_camera_index, cv2.CAP_DSHOW)

        def capture_frame():
            ret, frame = self.cap.read()

            if ret and frame is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    self.capture_and_save(frame)

                self.display_frame_on_canvas(frame)

                if cv2.waitKey(1) & 0xFF != ord('q'):
                    self.root.after(10, capture_frame)

        capture_frame()

    def display_frame_on_canvas(self, frame):
        if frame is not None:
            frame = cv2.resize(frame, (700, 500))

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            img_tk = ImageTk.PhotoImage(image=Image.fromarray(img_rgb))

            self.camera_canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            self.camera_canvas.image = img_tk

    def stop_capture_function(self):
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()

    def capture_and_save(self, frame):
        username = getpass.getuser()
        image_save_location = self.image_location_entry.get()

        if not image_save_location:
            messagebox.showerror("Error", "Please set the Image Save Location first.")
            return

        if not os.path.exists(image_save_location):
            os.makedirs(image_save_location)

        now = datetime.now()
        date_time = now.strftime("%Y%m%d_%H%M%S")
        file_name = f"EyeWatch_{date_time}.png"
        file_path = os.path.join(image_save_location, file_name)
        cv2.imwrite(file_path, frame)


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceCaptureApp(root)

    root.mainloop()
