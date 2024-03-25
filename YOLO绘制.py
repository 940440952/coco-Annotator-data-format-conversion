import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def show_image_and_yolo_annotations(image_dir, annotation_dir, image_id):
    # 颜色循环列表
    colors = ['red', 'yellow', 'blue', 'green']

    # 构建文件路径
    image_path = os.path.join(image_dir, f"{image_id}.jpg")
    annotation_path = os.path.join(annotation_dir, f"{image_id}.txt")

    # 读取图片
    image = plt.imread(image_path)

    # 创建画布
    fig, ax = plt.subplots(1)
    ax.imshow(image)

    # 检查标注文件是否存在
    if os.path.exists(annotation_path):
        with open(annotation_path, 'r') as file:
            for index, line in enumerate(file):
                parts = line.strip().split()

                # 检查是否有足够的数据来绘制边界框
                if len(parts) >= 5:
                    # YOLO 格式: class x_center y_center width height [keypoints...]
                    x_center, y_center, width, height = map(float, parts[1:5])
                    # 转换为 matplotlib 的坐标系
                    x = (x_center - width / 2) * image.shape[1]
                    y = (y_center - height / 2) * image.shape[0]
                    width = width * image.shape[1]
                    height = height * image.shape[0]

                    # 获取当前行的颜色
                    color = colors[index % len(colors)]

                    # 绘制边界框
                    rect = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor=color, facecolor='none')
                    ax.add_patch(rect)

                    # 处理关键点
                    if len(parts) > 5:
                        for i in range(5, len(parts), 3):
                            if parts[i] != "-" and parts[i + 1] != "-":
                                kp_x = float(parts[i]) * image.shape[1]
                                kp_y = float(parts[i + 1]) * image.shape[0]
                                circle = patches.Circle((kp_x, kp_y), radius=3, color=color)
                                ax.add_patch(circle)

    plt.show()

# 输入参数
image_dir = 'pic'  # 图片所在的文件夹路径
annotation_dir = 'merged_dataset'  # 标注所在的文件夹路径
image_id = '1079'  # 图片的编号，不包含文件扩展名

show_image_and_yolo_annotations(image_dir, annotation_dir, image_id)
