import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import numpy as np

class ImageBinarizationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("图像二值化工具")
        self.root.geometry("1000x700")
        
        # 初始化变量
        self.original_img = None
        self.display_img = None
        self.tk_img = None
        self.roi_coords = []
        self.is_drawing = False
        self.threshold = 127  # 默认阈值
        self.binary_img = None  # 存储二值化结果
        
        # 创建UI组件
        self.create_widgets()
        
    def create_widgets(self):
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="打开", command=self.open_image)
        filemenu.add_command(label="保存二值化图像", command=self.save_binary_image)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=filemenu)
        self.root.config(menu=menubar)
        
        # 创建主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建左侧图像显示区域
        left_frame = tk.Frame(main_frame, width=600, height=600)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(left_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        # 创建右侧控制面板
        right_frame = tk.Frame(main_frame, width=300, height=600)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=10)
        
        # 阈值调整
        threshold_frame = tk.Frame(right_frame)
        threshold_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(threshold_frame, text="二值化阈值:").pack(side=tk.LEFT)
        self.threshold_var = tk.IntVar(value=self.threshold)
        threshold_scale = tk.Scale(threshold_frame, from_=0, to=255, orient=tk.HORIZONTAL, 
                                  variable=self.threshold_var, command=self.update_threshold)
        threshold_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # 按钮区域
        button_frame = tk.Frame(right_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="二值化所选区域", command=self.binarize_selection).pack(fill=tk.X)
        tk.Button(button_frame, text="导出二值化图像", command=self.save_binary_image).pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="重置选择", command=self.reset_selection).pack(fill=tk.X, pady=5)
        
        # 信息显示区域
        self.info_label = tk.Label(right_frame, text="请打开一张图片开始操作", wraplength=280)
        self.info_label.pack(fill=tk.X, padx=10, pady=10)
        
        # 二值化结果显示
        result_frame = tk.Frame(right_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(result_frame, text="二值化结果:").pack(anchor=tk.W)
        self.result_canvas = tk.Canvas(result_frame, bg="white", width=280, height=200)
        self.result_canvas.pack(fill=tk.BOTH, expand=True)
        
    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("图像文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            try:
                self.original_img = Image.open(file_path)
                self.display_img = self.original_img.copy()
                self.update_canvas()
                self.info_label.config(text=f"已加载图片: {file_path}")
                self.reset_selection()
            except Exception as e:
                messagebox.showerror("错误", f"无法打开图片: {str(e)}")
    
    def update_canvas(self):
        if self.display_img:
            # 调整图像大小以适应画布
            canvas_width = self.canvas.winfo_width() or 600
            canvas_height = self.canvas.winfo_height() or 600
            
            img_width, img_height = self.display_img.size
            scale = min(canvas_width/img_width, canvas_height/img_height)
            new_size = (int(img_width * scale), int(img_height * scale))
            
            resized_img = self.display_img.resize(new_size, Image.LANCZOS)
            self.tk_img = ImageTk.PhotoImage(resized_img)
            
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
            
            # 如果有ROI，绘制它
            if len(self.roi_coords) == 4:
                x1, y1, x2, y2 = self.roi_coords
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)
    
    def on_mouse_down(self, event):
        if self.tk_img:
            self.is_drawing = True
            self.roi_coords = [event.x, event.y, event.x, event.y]
    
    def on_mouse_drag(self, event):
        if self.is_drawing and self.tk_img:
            self.roi_coords[2] = event.x
            self.roi_coords[3] = event.y
            self.update_canvas()
    
    def on_mouse_up(self, event):
        if self.is_drawing and self.tk_img:
            self.is_drawing = False
            self.roi_coords[2] = event.x
            self.roi_coords[3] = event.y
            
            # 确保坐标正确（x1 < x2, y1 < y2）
            self.roi_coords[0], self.roi_coords[2] = min(self.roi_coords[0], self.roi_coords[2]), max(self.roi_coords[0], self.roi_coords[2])
            self.roi_coords[1], self.roi_coords[3] = min(self.roi_coords[1], self.roi_coords[3]), max(self.roi_coords[1], self.roi_coords[3])
            
            self.update_canvas()
    
    def reset_selection(self):
        self.roi_coords = []
        self.update_canvas()
        self.result_canvas.delete("all")
        self.binary_img = None
        self.info_label.config(text="请框选要二值化的区域")
    
    def update_threshold(self, value):
        self.threshold = int(value)
    
    def binarize_selection(self):
        if not self.original_img or len(self.roi_coords) != 4:
            messagebox.showinfo("提示", "请先选择图片并框选区域")
            return
        
        # 获取原始图像的尺寸和缩放比例
        canvas_width = self.canvas.winfo_width() or 600
        canvas_height = self.canvas.winfo_height() or 600
        img_width, img_height = self.original_img.size
        scale = min(canvas_width/img_width, canvas_height/img_height)
        
        # 计算ROI在原始图像中的坐标
        x1, y1, x2, y2 = [int(coord / scale) for coord in self.roi_coords]
        
        # 确保坐标在有效范围内
        x1 = max(0, min(x1, img_width - 1))
        x2 = max(0, min(x2, img_width - 1))
        y1 = max(0, min(y1, img_height - 1))
        y2 = max(0, min(y2, img_height - 1))
        
        if x1 >= x2 or y1 >= y2:
            messagebox.showinfo("提示", "所选区域无效，请选择更大的区域")
            return
        
        # 提取ROI并转换为灰度图
        roi = self.original_img.crop((x1, y1, x2, y2))
        roi_gray = roi.convert("L")
        
        # 二值化处理
        threshold = self.threshold
        roi_binary = roi_gray.point(lambda p: 255 if p > threshold else 0)
        
        # 显示二值化结果
        self.display_binarized_result(roi_binary)
        
        # 保存二值化图像
        self.binary_img = roi_binary
        
        self.info_label.config(text=f"已完成二值化，阈值: {threshold}")
    
    def display_binarized_result(self, img):
        # 调整图像大小以适应结果画布
        canvas_width = 280
        canvas_height = 200
        
        img_width, img_height = img.size
        scale = min(canvas_width/img_width, canvas_height/img_height)
        new_size = (int(img_width * scale), int(img_height * scale))
        
        resized_img = img.resize(new_size, Image.NEAREST)
        tk_binary_img = ImageTk.PhotoImage(resized_img)
        
        self.result_canvas.delete("all")
        self.result_canvas.create_image(0, 0, anchor=tk.NW, image=tk_binary_img)
        self.result_canvas.image = tk_binary_img  # 保持引用防止被垃圾回收
    
    def save_binary_image(self):
        if self.binary_img is None:
            messagebox.showinfo("提示", "请先二值化一个区域")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG文件", "*.png"), ("JPEG文件", "*.jpg"), ("BMP文件", "*.bmp")]
        )
        
        if file_path:
            try:
                self.binary_img.save(file_path)
                messagebox.showinfo("成功", f"图像已保存到: {file_path}")
                self.info_label.config(text=f"已保存图像到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存图像: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageBinarizationTool(root)
    
    # 窗口大小调整时更新画布
    root.bind("<Configure>", lambda e: app.update_canvas() if app.display_img else None)
    
    root.mainloop()    