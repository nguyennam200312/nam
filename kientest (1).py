from PIL import ImageFont, ImageDraw, Image
import numpy as np
from tkinter import *
from tkinter.ttk import Combobox
from tkinter import filedialog
import tkinter
import cv2
from easyocr import Reader
from PIL import Image, ImageTk

wd = Tk()
wd.title("NHẬN DẠNG BIỂN SỐ XE")
wd.geometry("640x640")

lbl = Label(wd, text="NHẬN DẠNG BIỂN SỐ XE", fg="darkblue", font=("Monsterrat", 14))
lbl.pack(side=TOP, pady=10)

window = Frame(wd)
window.pack()
window1 = Frame(window)
window1.pack(side=TOP)
window2 = Frame(window)
window2.pack()

combo = Combobox(window1, state="readonly")
combo['values'] = ("Nhập ảnh", "Camera", "Video")
combo.current(0)
combo.pack(side=TOP, padx=5, pady=5, anchor=N)

label = Label(window)
label.pack(side=BOTTOM, fill=BOTH, expand=1)

reader = Reader(['en'])

def delete():
    for widget in window2.winfo_children():
        widget.destroy()

def detect_plate(image):
    image_resized = cv2.resize(image, (800, 600))
    gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    plate_contour = None
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            if w > 80 and h > 20:
                plate_contour = approx
                break

    if plate_contour is None:
        return image, "Không tìm thấy biển số xe"

    x, y, w, h = cv2.boundingRect(plate_contour)
    plate = gray[y:y + h, x:x + w]

    result = reader.readtext(plate)
    if len(result) == 0:
        text = "Không thấy biển số xe"
    else:
        text = result[0][1]

    cv2.drawContours(image_resized, [plate_contour], -1, (0, 255, 0), 3)
    
    image_pil = Image.fromarray(cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)
    font_path = "./times.ttf"
    font = ImageFont.truetype(font_path, 32)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    text_x = (image_pil.width - text_width) / 2
    text_y = (image_pil.height - text_height) / 2
    draw.text((text_x, text_y), text, font=font, fill=(0, 255, 0))

    result_image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    
    return result_image, text

def handleButton():
    if combo.get() == "Camera":
        video = cv2.VideoCapture(0)
        if not video.isOpened():
            raise RuntimeError("Không mở được camera")

        def show_frame():
            ret, frame = video.read()
            if not ret:
                return

            frame, text = detect_plate(frame)
            cv2.imshow("Camera", frame)

        while True:
            show_frame()
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        video.release()
        cv2.destroyAllWindows()

    elif combo.get() == "Video":
        filename = filedialog.askopenfilename(title="Chọn video", filetypes=[("mp4 files", "*.mp4"), ("mov files", "*.mov")])
        if not filename:
            return

        cap = cv2.VideoCapture(filename)
        if not cap.isOpened():
            raise RuntimeError("Không mở được video")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame, text = detect_plate(frame)
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

    elif combo.get() == "Nhập ảnh":
        filename = filedialog.askopenfilename(title="Chọn ảnh", filetypes=[("JPG files", "*.jpg"), ("JPEG files", "*.jpeg"), ("PNG files", "*.png")])
        if not filename:
            return

        image = Image.open(filename).convert("RGB")
        width, height = image.size
        if width > 800 or height > 500:
            ratio = min(500 / width, 500 / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height))

        icon = ImageTk.PhotoImage(image)
        label.configure(image=icon)
        label.image = icon

        delete()
        image_np = np.array(image)

        def show_frame():
            result_image, text = detect_plate(image_np)
            result_image_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(result_image_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            label.imgtk = imgtk
            label.configure(image=imgtk)
            print("Biển số: ", text)

        hienthilogo = Button(window2, text="Hiển thị kết quả", command=show_frame, activeforeground="darkblue")
        hienthilogo.pack(side=TOP, padx=5, pady=5)

btnNhap = Button(window1, text="Kiểm tra", command=handleButton, activeforeground="darkblue")
btnNhap.pack(side=TOP, padx=5, pady=5)

wd.mainloop()
