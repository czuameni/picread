import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pytesseract
import os
import csv

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class PicReadApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PicRead")
        self.geometry("900x600")

        self.iconbitmap("icon.ico")

        self.image_path = None
        self.image_preview = None

        self.create_ui()

    def create_ui(self):
        left_frame = ctk.CTkFrame(self, width=200)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.upload_btn = ctk.CTkButton(left_frame, text="Upload Image", command=self.upload_image)
        self.upload_btn.pack(pady=10)

        self.language_var = ctk.StringVar(value="eng")

        self.lang_menu = ctk.CTkOptionMenu(
            left_frame,
            values=["eng", "pol", "spa"],
            variable=self.language_var
        )
        self.lang_menu.pack(pady=10)

        self.extract_btn = ctk.CTkButton(left_frame, text="Extract Text", command=self.extract_text)
        self.extract_btn.pack(pady=10)

        right_frame = ctk.CTkFrame(self)
        right_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.image_label = ctk.CTkLabel(right_frame, text="No image loaded")
        self.image_label.pack(expand=True)

        self.textbox = ctk.CTkTextbox(self, height=150)
        self.textbox.pack(fill="both", padx=10, pady=10)

        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", padx=10, pady=5)

        self.copy_btn = ctk.CTkButton(bottom_frame, text="Copy", command=self.copy_text)
        self.copy_btn.pack(side="left", padx=5)

        self.save_txt_btn = ctk.CTkButton(bottom_frame, text="Save TXT", command=self.save_txt)
        self.save_txt_btn.pack(side="left", padx=5)

        self.save_csv_btn = ctk.CTkButton(bottom_frame, text="Save CSV", command=self.save_csv)
        self.save_csv_btn.pack(side="left", padx=5)

        self.status = ctk.CTkLabel(self, text="Status: Ready", anchor="w")
        self.status.pack(fill="x", padx=10, pady=5)

    def set_status(self, text):
        self.status.configure(text=f"Status: {text}")
        self.update_idletasks()

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )

        if not file_path:
            return

        try:
            image = Image.open(file_path)
        except Exception:
            messagebox.showerror("Error", "Invalid image file.")
            return

        self.image_path = file_path

        image.thumbnail((400, 400))
        self.image_preview = ImageTk.PhotoImage(image)

        self.image_label.configure(image=self.image_preview, text="")
        self.set_status("Image loaded")

    def extract_text(self):
        if not self.image_path:
            messagebox.showwarning("Warning", "No image selected.")
            return

        self.set_status("Extracting...")

        try:
            image = Image.open(self.image_path)
            text = pytesseract.image_to_string(image, lang=self.language_var.get())

        except pytesseract.TesseractError:
            messagebox.showerror("Error", "Selected language is not installed.")
            self.set_status("Error")
            return

        except pytesseract.TesseractNotFoundError:
            messagebox.showerror("Error", "Tesseract is not installed or not in PATH.")
            self.set_status("Error")
            return

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Error")
            return

        self.textbox.delete("1.0", "end")

        if text.strip() == "":
            self.textbox.insert("end", "[No text detected]")
            self.set_status("No text found")
        else:
            self.textbox.insert("end", text)
            self.set_status("Done")

    def copy_text(self):
        text = self.textbox.get("1.0", "end").strip()
        if not text:
            return

        self.clipboard_clear()
        self.clipboard_append(text)
        self.set_status("Copied to clipboard")

    def save_txt(self):
        text = self.textbox.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Warning", "No text to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt")

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            self.set_status("Saved as TXT")

    def save_csv(self):
        text = self.textbox.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Warning", "No text to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv")

        if file_path:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for line in text.splitlines():
                    writer.writerow([line])
            self.set_status("Saved as CSV")


if __name__ == "__main__":
    app = PicReadApp()
    app.mainloop()
