import numpy as np
from pycocotools import mask as maskUtils
from skimage import measure
import json
import os
from typing import List
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2

# 类别标签及其索引
class_labels = [
    "1st distal phalanx",
    "1st metacarpal",
    "1st proximal phalanx",
    "3rd distal phalanx",
    "3rd metacarpal",
    "3rd middle phalanx",
    "3rd proximal phalanx",
    "5th distal phalanx",
    "5th metacarpal",
    "5th middle phalanx",
    "5th proximal phalanx",
    "capitate",
    "hamate",
    "radius"
]

# 创建类别标签到索引的映射
label_to_index = {label: index for index, label in enumerate(class_labels)}


def draw_polygon_on_image(image_path, polygon):
    # 加载图片
    img = Image.open(image_path)
    fig, ax = plt.subplots(1)
    ax.imshow(img)

    # 创建多边形
    polygon_shape = patches.Polygon(np.array(polygon).reshape(-1, 2), fill=False, edgecolor='r')
    ax.add_patch(polygon_shape)

    plt.show()


def draw_polygons_on_image(image_path, polygons):
    # 加载图片
    img = Image.open(image_path)
    fig, ax = plt.subplots(1)
    ax.imshow(img)

    # 创建多边形并添加到图像上
    for polygon in polygons:
        polygon_shape = patches.Polygon(np.array(polygon).reshape(-1, 2), fill=False, edgecolor='r')
        ax.add_patch(polygon_shape)

    plt.show()


class InputStream:
    def __init__(self, data):
        self.data = data
        self.i = 0

    def read(self, size):
        out = self.data[self.i:self.i + size]
        self.i += size
        return int(out, 2)


def access_bit(data, num):
    """ from bytes array to bits by num position"""
    base = int(num // 8)
    shift = 7 - int(num % 8)
    return (data[base] & (1 << shift)) >> shift


def bytes2bit(data):
    """ get bit string from bytes data"""
    return ''.join([str(access_bit(data, i)) for i in range(len(data) * 8)])


def rle_to_mask(rle: List[int], height: int, width: int) -> np.array:
    """
    Converts rle to image mask
    Args:
        rle: your long rle
        height: original_height
        width: original_width

    Returns: np.array
    """

    rle_input = InputStream(bytes2bit(rle))

    num = rle_input.read(32)
    word_size = rle_input.read(5) + 1
    rle_sizes = [rle_input.read(4) + 1 for _ in range(4)]
    # print('RLE params:', num, 'values,', word_size, 'word_size,', rle_sizes, 'rle_sizes')

    i = 0
    out = np.zeros(num, dtype=np.uint8)
    while i < num:
        x = rle_input.read(1)
        j = i + 1 + rle_input.read(rle_sizes[rle_input.read(2)])
        if x:
            val = rle_input.read(word_size)
            out[i:j] = val
            i = j
        else:
            while i < j:
                val = rle_input.read(word_size)
                out[i] = val
                i += 1

    image = np.reshape(out, [height, width, 4])[:, :, 3]
    return image


def binary_mask_to_polygon(binary_mask, tolerance=2.0):
    """Convert a binary mask to a list of polygons."""
    # Convert binary mask to boolean array
    binary_mask = binary_mask.astype(np.uint8)

    # Find contours
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    polygons = []
    for contour in contours:
        # Simplify contour
        polygon = cv2.approxPolyDP(contour, tolerance, True)

        # Convert polygon to expected format
        polygon = [(point[0][0], point[0][1]) for point in polygon]

        polygons.append(polygon)

    return polygons


def normalize_polygons(polygons, width, height):
    """将多边形坐标归一化为[0, 1]范围."""
    normalized_polygons = []
    for polygon in polygons:
        normalized_polygon = []
        for x, y in polygon:
            normalized_x = x / width
            normalized_y = y / height
            normalized_polygon.append(normalized_x)
            normalized_polygon.append(normalized_y)
        normalized_polygons.append(normalized_polygon)
    return normalized_polygons


def show_mask_on_image(image_path, mask):
    # 加载图片
    img = Image.open(image_path)
    fig, ax = plt.subplots(1)
    ax.imshow(img)

    # 在图片上显示mask
    ax.imshow(mask, cmap='jet', alpha=0.5)  # 使用透明度来看到图片和mask的叠加效果

    plt.show()


def convert_rle_to_yolo(json_file, output_dir):
    """将RLE格式转换为YOLO格式并保存."""
    with open(json_file, 'r') as file:
        data = json.load(file)

    for item in data:
        file_name = item['file_upload']
        image_id = os.path.splitext(file_name)[0].split('-')[-1]
        annotations = item['annotations'][0]
        results1 = annotations['result']
        yolo_format_lines = []
        for r in results1:
            # 如果r['type']!="brushlabels"则跳过
            if r['type'] != "brushlabels":
                continue
            original_width = r['original_width']
            original_height = r['original_height']
            rle = r['value']['rle']
            label = r['value']['brushlabels'][0]  # 类别标签
            class_index = label_to_index[label]  # 获取类别索引

            mask = rle_to_mask(rle, original_height, original_width)
            polygons = binary_mask_to_polygon(mask)
            # draw_polygons_on_image("images/" + file_name, polygons)
            normalized_polygons = normalize_polygons(polygons, original_width, original_height)

            # normalized_polygons中的所有数列拼接在一起
            one_dim_list = [item for sublist in normalized_polygons for item in sublist]
            yolo_format_line = str(class_index) + ' ' + ' '.join([str(elem) for elem in one_dim_list])

            yolo_format_lines.append(yolo_format_line)

        output_file = os.path.join(output_dir, f"{image_id}.txt")
        with open(output_file, 'w') as out_file:
            out_file.write("\n".join(yolo_format_lines))


# 调用函数进行转换
json_file = 'brush.json'
output_dir = 'yolo_labels_segmentation'
os.makedirs(output_dir, exist_ok=True)
convert_rle_to_yolo(json_file, output_dir)
