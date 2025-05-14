import tkinter as tk
from PIL import Image, ImageTk
import cv2
import subprocess
import argparse
import os

class MicroscopioApp:
    def __init__(self, window, window_title, fullscreen=False):
        self.window = window
        self.window.title(window_title)
        self.fullscreen = fullscreen
        if self.fullscreen:
            self.window.attributes('-fullscreen', True)

        self.cap = cv2.VideoCapture(0)  # 0 indica la webcam predefinita, potrebbe cambiare
        if not self.cap.isOpened():
            print("Impossibile aprire la webcam")
            self.window.quit()

        self.canvas = tk.Canvas(window, width=window.winfo_screenwidth(), height=window.winfo_screenheight())
        self.canvas.pack()

        self.photo = None
        self.update_frame()

        # Pulsante di spegnimento in basso a destra (sempre presente)
        button_width = 10
        button_height = 2
        button_x = window.winfo_screenwidth() - (button_width * 10) - 20
        button_y = window.winfo_screenheight() - (button_height * 20) - 20
        self.shutdown_button = tk.Button(window, text="Spegni", command=self.show_shutdown_popup,
                                          width=button_width, height=button_height, font=("Arial", 14))
        self.shutdown_button.place(x=button_x, y=button_y)

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Converti il frame OpenCV in un'immagine PIL
            self.cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.pil_img = Image.fromarray(self.cv2_img)
            # Ridimensiona l'immagine per adattarla alla finestra/schermo mantenendo le proporzioni
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            img_width, img_height = self.pil_img.size

            width_ratio = screen_width / img_width
            height_ratio = screen_height / img_height

            if width_ratio > height_ratio:
                new_width = int(img_width * height_ratio)
                new_height = screen_height
            else:
                new_width = screen_width
                new_height = int(img_height * width_ratio)

            resized_img = self.pil_img.resize((new_width, new_height))
            self.photo = ImageTk.PhotoImage(resized_img)
            self.canvas.create_image(screen_width // 2, screen_height // 2, image=self.photo, anchor=tk.CENTER)
        self.window.after(30, self.update_frame)  # Aggiorna ogni 30 millisecondi

    def show_shutdown_popup(self):
        popup = tk.Toplevel(self.window)
        popup.title("Conferma Spegnimento")
        label = tk.Label(popup, text="Sei sicuro di voler spegnere il sistema?")
        label.pack(padx=20, pady=10)
        confirm_button = tk.Button(popup, text="Sì, Spegni", command=self.shutdown_system)
        confirm_button.pack(pady=5)
        cancel_button = tk.Button(popup, text="Annulla", command=popup.destroy)
        cancel_button.pack(pady=5)

    def shutdown_system(self):
        self.cap.release()
        subprocess.run(["sudo", "shutdown", "-h", "now"])

    def on_closing(self):
        self.cap.release()
        self.window.destroy()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualizza il feed del microscopio con opzione fullscreen.")
    parser.add_argument("--fullscreen", action="store_true", help="Avvia l'applicazione a schermo intero.")
    args = parser.parse_args()

    root = tk.Tk()
    app = MicroscopioApp(root, "Microscopio", fullscreen=args.fullscreen)
