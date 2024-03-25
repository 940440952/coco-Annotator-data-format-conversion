import tkinter as tk
from tkinter import filedialog, Listbox, Scrollbar, messagebox
from PIL import Image, ImageTk
import os

class AnnotationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("标注工具")

        self.scale = 1
        self.offset_x = 0
        self.offset_y = 0
        self.canvas_width = 1000
        self.canvas_height = 600

        root.geometry(f"{self.canvas_width}x{self.canvas_height}")

        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.image_dir_label = tk.Label(self.top_frame, text="图片目录: 未选择")
        self.image_dir_label.pack(side=tk.LEFT)

        self.annotation_dir_label = tk.Label(self.top_frame, text="标注目录: 未选择")
        self.annotation_dir_label.pack(side=tk.LEFT)

        self.load_image_button = tk.Button(self.top_frame, text="图片目录", command=self.load_image_directory)
        self.load_image_button.pack(side=tk.LEFT)

        self.load_annotation_button = tk.Button(self.top_frame, text="标注目录", command=self.load_annotation_directory)
        self.load_annotation_button.pack(side=tk.LEFT)

        self.load_button = tk.Button(self.top_frame, text="加载", command=self.load_content)
        self.load_button.pack(side=tk.LEFT)

        self.list_frame = tk.Frame(root)
        self.list_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = Listbox(self.list_frame, width=50)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.Y)

        scrollbar = Scrollbar(self.list_frame, command=self.file_listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)

        self.image_dir = None
        self.annotation_dir = None
        self.image_list = []
        self.photo_image = None
        self.annotation_data = []
        self.canvas.bind('<Configure>', lambda e: self.update_image_canvas())

    def load_image_directory(self):
        self.image_dir = filedialog.askdirectory(title="选择图片目录")
        self.image_dir_label.config(text=f"图片目录: {self.image_dir}")

    def load_annotation_directory(self):
        self.annotation_dir = filedialog.askdirectory(title="选择标注目录")
        self.annotation_dir_label.config(text=f"标注目录: {self.annotation_dir}")

    def load_content(self):
        if not self.image_dir or not self.annotation_dir:
            messagebox.showerror("错误", "请先选择图片目录和标注目录")
            return

        self.image_list = [f for f in os.listdir(self.image_dir) if f.endswith('.jpg')]
        self.file_listbox.delete(0, tk.END)
        for filename in self.image_list:
            annotation_path = os.path.join(self.annotation_dir, filename.replace('.jpg', '.txt'))
            has_annotation = "有标注" if os.path.exists(annotation_path) else "无标注"
            self.file_listbox.insert(tk.END, f"{filename} - {has_annotation}")

    def on_file_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            filename = self.image_list[index]
            self.load_image(filename)

    def load_image(self, filename):
        image_path = os.path.join(self.image_dir, filename)
        self.current_image = Image.open(image_path)

        # 计算缩放比例
        original_width, original_height = self.current_image.size
        scale_w = self.canvas_width / original_width
        scale_h = self.canvas_height / original_height
        self.scale = min(scale_w, scale_h)

        # 根据缩放比例调整图像尺寸
        new_width = int(original_width * self.scale)
        new_height = int(original_height * self.scale)
        self.photo_image = ImageTk.PhotoImage(
            self.current_image.resize((new_width, new_height), Image.Resampling.LANCZOS))

        # 计算偏移量以在画布上居中图像
        self.offset_x = (self.canvas_width - new_width) // 2
        self.offset_y = (self.canvas_height - new_height) // 2

        self.canvas.create_image(self.offset_x, self.offset_y, image=self.photo_image, anchor='nw')

        # 加载并绘制注释
        annotation_path = os.path.join(self.annotation_dir, filename.replace('.jpg', '.txt'))
        if os.path.exists(annotation_path):
            self.load_annotations(annotation_path)

    def load_annotations(self, annotation_path):
        self.annotation_data.clear()
        with open(annotation_path, 'r') as file:
            for line in file:
                parts = line.split()
                if len(parts) < 5:
                    continue  # 不是有效的标注行

                bbox = [float(n) for n in parts[1:5]]
                keypoints = [(float(parts[i]), float(parts[i + 1]))
                             for i in range(5, len(parts), 3)]
                self.annotation_data.append((bbox, keypoints))

        self.draw_annotations()

    def update_image_canvas(self):
        # Only proceed if an image has been loaded
        if hasattr(self, 'current_image') and self.current_image:
            self.canvas.delete("all")  # Clear the canvas of all content

            # Get the canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Calculate the image size after proportional scaling
            img_width, img_height = self.current_image.size
            scale_w = canvas_width / img_width
            scale_h = canvas_height / img_height
            self.scale = min(scale_w, scale_h)
            new_width = int(img_width * self.scale)
            new_height = int(img_height * self.scale)

            # Resize the image
            img_resized = self.current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(img_resized)

            # Calculate the offset to center the image
            self.offset_x = (canvas_width - new_width) // 2
            self.offset_y = (canvas_height - new_height) // 2

            # Display the image at the center of the canvas
            self.canvas.create_image(self.offset_x, self.offset_y, image=self.photo_image, anchor='nw')

            # Redraw the annotations
            self.draw_annotations()

    def draw_annotations(self):
        if not self.annotation_data or not self.photo_image:
            return

        self.canvas.delete("annotation")  # 删除旧的注释
        for bbox, keypoints in self.annotation_data:
            # 转换并绘制边界框
            x1, y1 = ((bbox[0] - bbox[2] / 2) * self.photo_image.width() + self.offset_x,
                      (bbox[1] - bbox[3] / 2) * self.photo_image.height() + self.offset_y)
            x2, y2 = ((bbox[0] + bbox[2] / 2) * self.photo_image.width() + self.offset_x,
                      (bbox[1] + bbox[3] / 2) * self.photo_image.height() + self.offset_y)
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", tags="annotation")

            # 转换并绘制关键点
            for kp in keypoints:
                kp_x = (kp[0] * self.photo_image.width() + self.offset_x)
                kp_y = (kp[1] * self.photo_image.height() + self.offset_y)
                self.canvas.create_oval(kp_x - 3, kp_y - 3, kp_x + 3, kp_y + 3, fill="blue", tags="annotation")

if __name__ == "__main__":
    root = tk.Tk()
    app = AnnotationApp(root)
    root.mainloop()

