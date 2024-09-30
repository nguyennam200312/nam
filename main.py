import numpy 
from tkinter import *
from tkinter.ttk import * #chua combobox
from tkinter import filedialog
import tkinter
import cv2
from ultralytics import YOLO
from PIL import Image, ImageTk
wd = tkinter.Tk()
wd.title("NHẬN DẠNG LOGO CÁC HÃNG XE Ô TÔ")
wd.geometry("640x640")

#thêm label
lbl = tkinter.Label(wd, text = "NHẬN DẠNG LOGO CÁC HÃNG XE Ô TÔ", fg = "darkblue", font=("Monsterrat"))
lbl.pack(side=TOP)

window = Frame(wd)
window.pack()
window1 = Frame(window)
window1.pack(side=TOP)
window2 = Frame(window)
window2.pack()

#thêm combobox
combo = Combobox(window1,state="readonly" )
combo['values'] = ("Nhập ảnh","Camera","Video")
combo.current(0)
combo.pack(side=TOP, padx=5, pady=5, anchor=N)
global video
# Tạo widget Label rỗng hiện ảnh gốc
label = tkinter.Label(window)
label.pack(side=BOTTOM,fill=BOTH,expand=1)

model = YOLO("nhandanglogo/nhandanglogo/best.pt")
class_names = ["Vinfast","Toyota","Nissan","KIA","Hyundai","Ford","Honda","Peugeot","Suzuki","Audi",
               "BMW","Porsche","Mitsubishi","Lexus","Mercedes-benz","Mazda","Volkswagen","Subaru" ]


def delete():
    # Lấy danh sách các widget con của cửa sổ
    list = window2.pack_slaves()
    # Xóa từng widget con
    for l in list:
        l.pack_forget()
def handleButton():
    if combo.get()=="Camera":
        video = cv2.VideoCapture(0)  # mở camera
        canvas_w = video.get(cv2.CAP_PROP_FRAME_WIDTH) // 2  # do phân giải bằng 1/2 camera
        canvas_h = video.get(cv2.CAP_PROP_FRAME_HEIGHT) // 2
        canvas = tkinter.Canvas(wd, width=canvas_w, height=canvas_h)
        canvas.pack()

        def show_frame():
            results = model(source=frame, stream=True)
            cv2.waitKey(1)
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    if box.conf > 0.4:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
                        cv2.putText(frame, class_names[int(box.cls.item())] + " " + "{:.2f}".format(box.conf.item()),
                                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5, (255, 0, 255), 2)  # ghi tên lớp
                cv2.imshow("Camera", frame)
        while True:  # lặp vô hạn
            ret, frame = video.read()  # đọc một khung hình từ video
            if not ret:  # nếu không đọc được thì thoát
                break
            show_frame()
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        video.release()
        cv2.destroyAllWindows()
    ##############################################################
    if combo.get() == "Video":
        filename = filedialog.askopenfilename(title="Chọn video", filetypes=[("mp4 files", "*.mp4"), ("mp4 files", "*.mov")])
        print("Đã chọn:", filename)

        # Open the video file
        cap = cv2.VideoCapture(filename)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # giảm kích thước bộ đệm
        # Lấy kích thước khung hình ban đầu
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # Tính toán kích thước mới dựa trên tỷ lệ
        if height > 640:
            ratio = min(640 / width, 640 / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)

        frame_skip_interval = 10  # Số frame bỏ qua
        frame_no = 0  # biến đếm số frame

        while True:
            # Đọc frame từ video
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)  # nhảy qua một số frame không cần thiết
            ret, frame = cap.read()
            if not ret:
                # Khi video kết thúc, thoát khỏi vòng lặp
                break

            # Thay đổi kích thước frame
            frame = cv2.resize(frame, (new_width, new_height),
                               interpolation=cv2.INTER_LINEAR)  # sử dụng phương pháp nội suy tuyến tính

            results = model(source=frame, stream=True)
            cv2.waitKey(1)

            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    if box.conf > 0.75:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
                        cv2.putText(frame, class_names[int(box.cls.item())] + " " + "{:.2f}".format(box.conf.item()),
                                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.65, (255, 0, 255), 2)  # ghi tên lớp

            # Hiển thị frame
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            frame_no +=  frame_skip_interval   # tăng biến đếm số frame
        cap.release()
        cv2.destroyAllWindows()
#######################################################################################
    if combo.get()=="Nhập ảnh":
        # Mở hộp thoại chọn file và lấy đường dẫn của file ảnh
        filename = filedialog.askopenfilename(title="Chọn ảnh", filetypes=
        [("JPG files", "*.jpg"), ("JPEG files", "*.jpeg"),("PNG files", "*.png")])
        image = Image.open(filename)
        delete()
        image = image.convert("RGB")
        # Thêm code để thay đổi kích thước ảnh nếu lớn hơn
        width, height = image.size  # Lấy kích thước của ảnh
        if width > 800 or height > 500:
            ratio = min(500 / width, 500 / height)
            new_width = int(width * ratio)  # Tính chiều rộng mới
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height))  # Thay đổi kích thước ảnh

        icon = ImageTk.PhotoImage(image)
        # Gán đối tượng PhotoImage cho widget Label
        label.configure(image=icon)
        # Lưu lại đối tượng PhotoImage để tránh bị thu hồi bộ nhớ
        label.image = icon
        # Thêm code để sử dụng model cho ảnh và lưu kết quả vào biến results

        image = numpy.array(image)
        def handleButton1():
            show_frame()  # gọi hàm hiển thị

        hienthilogo = tkinter.Button(window2,text="Hiển thị kết quả",command=handleButton1,activeforeground="darkblue")
        hienthilogo.pack(side=TOP, padx=5, pady=5)
        def show_frame():
            results = model.predict(image)  # dự đoán các đối tượng trong ảnh
            for r in results:
                boxes = r.boxes  # lấy các hộp giới hạn
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 255), 2)
                    cv2.putText(image, class_names[int(box.cls.item())] +" "+ "{:.2f}".format(box.conf.item()),
                                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 0, 255), 2)

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            cv2.imshow("Image", image_rgb)  # hiển thị ảnh

#thêm button
btnNhap = tkinter.Button(window1, text="Kiểm tra", command=handleButton,activeforeground = "darkblue")
btnNhap.pack(side=TOP, padx=5, pady=5)

wd.mainloop()