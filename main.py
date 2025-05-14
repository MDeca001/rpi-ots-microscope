import tkinter as tk
from PIL import Image, ImageTk
import cv2
import argparse
import os
import time  # Import per i log con timestamp

class MicroscopioApp:
    def __init__(self, window, window_title, fullscreen=False, width=None, height=None):
        self.window = window
        self.window.title(window_title)
        self.fullscreen = fullscreen
        if self.fullscreen:
            self.window.attributes('-fullscreen', True)
            print(f"DEBUG: Avvio in modalità schermo intero.")
        else:
            print(f"DEBUG: Avvio in modalità finestra.")

        self.camera_index = 0
        print(f"DEBUG: Tentativo di apertura della webcam con indice {self.camera_index}.")
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            print(f"ERRORE: Impossibile aprire la webcam con indice {self.camera_index}.")
            self.window.quit()
            return

        print(f"DEBUG: Webcam aperta con successo.")

        if width is not None and height is not None:
            print(f"DEBUG: Tentativo di impostare la risoluzione della webcam a {width}x{height}.")
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"DEBUG: Risoluzione della webcam impostata (richiesta: {width}x{height}, effettiva: {actual_width}x{actual_height}).")
        else:
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"DEBUG: Risoluzione corrente della webcam: {actual_width}x{actual_height}.")

        self.canvas = tk.Canvas(window, width=window.winfo_screenwidth(), height=window.winfo_screenheight())
        self.canvas.pack()

        self.photo = None
        self.update_frame()

        # Pulsante per terminare il programma in basso a destra
        button_width = 12
        button_height = 2
        button_x = window.winfo_screenwidth() - (button_width * 10) - 20
        button_y = window.winfo_screenheight() - (button_height * 20) - 20
        self.quit_button = tk.Button(window, text="Termina", command=self.safe_quit,
                                     width=button_width, height=button_height, font=("Arial", 14))
        self.quit_button.place(x=button_x, y=button_y)
        print(f"DEBUG: Pulsante 'Termina' creato in posizione ({button_x}, {button_y}).")

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        print(f"DEBUG: Gestore per la chiusura della finestra impostato.")
        self.window.mainloop()
        print(f"DEBUG: Loop principale di Tkinter terminato.")

    def update_frame(self):
        start_time = time.time()
        ret, frame = self.cap.read()
        end_time_read = time.time()
        read_duration = (end_time_read - start_time) * 1000  # in millisecondi

        if ret:
            # Converti il frame OpenCV in un'immagine PIL
            self.cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(self.cv2_img)
            img_width, img_height = pil_img.size

            # Ridimensiona l'immagine per adattarla alla finestra/schermo mantenendo le proporzioni
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()

            width_ratio = screen_width / img_width
            height_ratio = screen_height / img_height

            if width_ratio > height_ratio:
                new_width = int(img_width * height_ratio)
                new_height = screen_height
            else:
                new_width = screen_width
                new_height = int(img_height * width_ratio)

            resized_img = pil_img.resize((new_width, new_height))
            self.photo = ImageTk.PhotoImage(resized_img)
            self.canvas.create_image(screen_width // 2, screen_height // 2, image=self.photo, anchor=tk.CENTER)
            end_time_display = time.time()
            display_duration = (end_time_display - end_time_read) * 1000  # in millisecondi
            # print(f"DEBUG: Frame aggiornato (lettura: {read_duration:.2f}ms, display: {display_duration:.2f}ms, risoluzione originale: {img_width}x{img_height}, ridimensionata a: {new_width}x{new_height}).")
            self.window.after(30, self.update_frame)  # Aggiorna ogni 30 millisecondi
        else:
            print(f"AVVISO: Nessun frame letto dalla webcam. Riprovo.")
            self.window.after(30, self.update_frame)

    def safe_quit(self):
        print(f"DEBUG: Richiesta di terminazione sicura del programma.")
        self.cap.release()
        print(f"DEBUG: Risorsa webcam rilasciata.")
        self.window.destroy()
        print(f"DEBUG: Finestra distrutta.")

    def on_closing(self):
        print(f"DEBUG: Chiusura della finestra rilevata.")
        self.safe_quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualizza il feed del microscopio con opzioni di fullscreen e risoluzione.")
    parser.add_argument("--fullscreen", action="store_true", help="Avvia l'applicazione a schermo intero.")
    parser.add_argument("--width", type=int, help="Forza la larghezza della risoluzione della webcam.")
    parser.add_argument("--height", type=int, help="Forza l'altezza della risoluzione della webcam.")
    args = parser.parse_args()

    root = tk.Tk()
    app = MicroscopioApp(root, "Microscopio", fullscreen=args.fullscreen, width=args.width, height=args.height)
