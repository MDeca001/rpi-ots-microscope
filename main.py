import tkinter as tk
from PIL import Image, ImageTk
import cv2
import argparse
import os
import time

# --- CONFIGURAZIONE INIZIALE ---
INIZIAL_ZOOM_PERCENTAGE = 1  # Percentuale della larghezza dello schermo per la dimensione iniziale del feed
WEBCAM_RESOLUTION_WIDTH = 640
WEBCAM_RESOLUTION_HEIGHT = 360
# -----------------------------

class MicroscopioApp(tk.Tk):
    def __init__(self, window_title, fullscreen=False):
        super().__init__()
        self.title(window_title)
        self.fullscreen = fullscreen

        self.larghezza_rettangolo = 0
        self.altezza_rettangolo = 0

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        if self.fullscreen:
            self.attributes('-fullscreen', True)
            print(f"DEBUG: Avvio in modalità schermo intero.")
            self.larghezza_rettangolo = screen_width
            self.altezza_rettangolo = screen_height
            self.canvas = tk.Canvas(self, bg="lightgray", width=screen_width, height=screen_height)
        else:
            print(f"DEBUG: Avvio in modalità finestra massimizzata.")
            self.state('zoomed') # Avvia la finestra massimizzata

            # Calcola le dimensioni del rettangolo 16:9 basate sulla dimensione dello schermo massimizzata
            larghezza_desiderata = int(screen_width * INIZIAL_ZOOM_PERCENTAGE)
            altezza_desiderata = int(larghezza_desiderata * 9 / 16)

            # Assicurati che l'altezza non superi una certa frazione dell'altezza dello schermo
            max_altezza_percentuale = 0.7 # Aumentato per lasciare più spazio verticale
            if altezza_desiderata > screen_height * max_altezza_percentuale:
                altezza_desiderata = int(screen_height * max_altezza_percentuale)
                larghezza_desiderata = int(altezza_desiderata * 16 / 9)

            self.larghezza_rettangolo = larghezza_desiderata
            self.altezza_rettangolo = altezza_desiderata
            self.canvas = tk.Canvas(self, bg="lightgray", width=self.larghezza_rettangolo, height=self.altezza_rettangolo)

        self.canvas.pack()
        self.video_label = self.canvas.create_image(self.larghezza_rettangolo // 2, self.altezza_rettangolo // 2, anchor=tk.CENTER)
        self.pulsante1 = tk.Button(self, text="Pulsante 1")
        self.pulsante2 = tk.Button(self, text="Pulsante 2")

        # Posiziona i pulsanti sotto il rettangolo, occupando la piena larghezza
        pulsante_altezza = 30
        spazio_tra_rettangolo_e_pulsanti = 10
        y_pulsanti = self.altezza_rettangolo + spazio_tra_rettangolo_e_pulsanti

        # Posiziona il primo pulsante a sinistra, occupando metà della larghezza
        larghezza_pulsante = screen_width // 2
        x_pulsante1 = 0
        self.pulsante1.place(x=x_pulsante1, y=y_pulsanti, width=larghezza_pulsante, height=pulsante_altezza)

        # Posiziona il secondo pulsante a destra, occupando metà della larghezza
        x_pulsante2 = larghezza_pulsante
        self.pulsante2.place(x=x_pulsante2, y=y_pulsanti, width=larghezza_pulsante, height=pulsante_altezza)

        self.camera_index = 0
        print(f"DEBUG: Tentativo di apertura della webcam con indice {self.camera_index}.")
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            print(f"ERRORE: Impossibile aprire la webcam con indice {self.camera_index}.")
            self.quit()
            return

        print(f"DEBUG: Webcam aperta con successo.")

        # Forza la risoluzione configurabile della webcam
        print(f"DEBUG: Tentativo di forzare la risoluzione della webcam a {WEBCAM_RESOLUTION_WIDTH}x{WEBCAM_RESOLUTION_HEIGHT}.")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_RESOLUTION_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCAM_RESOLUTION_HEIGHT)
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"DEBUG: Risoluzione della webcam impostata (richiesta: {WEBCAM_RESOLUTION_WIDTH}x{WEBCAM_RESOLUTION_HEIGHT}, effettiva: {actual_width}x{actual_height}).")

        self.update_frame()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        print(f"DEBUG: Gestore per la chiusura della finestra impostato.")
        print(f"DEBUG: Loop principale di Tkinter avviato.")
        self.mainloop()
        print(f"DEBUG: Loop principale di Tkinter terminato.")

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(self.cv2_img)
            # Ridimensiona l'immagine alla dimensione fissa del rettangolo
            resized_img = pil_img.resize((self.larghezza_rettangolo, self.altezza_rettangolo))
            self.photo = ImageTk.PhotoImage(resized_img)
            self.canvas.itemconfig(self.video_label, image=self.photo)
        self.after(30, self.update_frame)

    def safe_quit(self):
        print(f"DEBUG: Richiesta di terminazione sicura del programma.")
        self.cap.release()
        print(f"DEBUG: Risorsa webcam rilasciata.")
        self.destroy()
        print(f"DEBUG: Finestra distrutta.")

    def on_closing(self):
        print(f"DEBUG: Chiusura della finestra rilevata.")
        self.safe_quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualizza il feed del microscopio.")
    parser.add_argument("--fullscreen", action="store_true", help="Avvia l'applicazione a schermo intero.")
    args = parser.parse_args()

    app = MicroscopioApp("Microscopio", fullscreen=args.fullscreen)
