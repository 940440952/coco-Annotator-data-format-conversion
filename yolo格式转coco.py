import os
import json
from PIL import Image

# 文件夹路径
annotation_path = 'D:/WorkSapce/数据集转换/merged_dataset'
pic_path = 'D:/WorkSapce/数据集转换/pic'

# 初始化COCO数据结构
coco_data = {
    "images": [],
    "annotations": [],
    "categories": [
        {
            "id": 19,
            "name": "安全带速插人体关键点",
            "supercategory": "",
            "keypoints": [
                "安全带1", "安全带2", "安全带3", "安全带4", "安全带5", "安全带6", "安全带7", "安全带8", "安全带9",
                "速插1", "速插2", "速插3", "速插4", "速插5", "速插6", "速插7", "速插8", "速插9",
                "0_nose", "1_left_eye", "2_right_eye", "3_left_ear", "4_right_ear", "5_left_shoulder",
                "6_right_shoulder", "7_left_elbow", "8_right_elbow", "9_left_wrist", "10_right_wrist",
                "11_left_hip", "12_right_hip", "13_left_knee", "14_right_knee", "15_left_ankle", "16_right_ankle"
            ],
            "skeleton": [
                [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8], [8, 9], [10, 11], [11, 12], [12, 13],
                [13, 14], [14, 15], [15, 16], [16, 17], [17, 18], [19, 20], [19, 21], [20, 22], [21, 23],
                [22, 24], [23, 25], [24, 25], [24, 26], [24, 30], [25, 27], [25, 31], [26, 28], [27, 29],
                [30, 31], [30, 32], [31, 33], [32, 34], [33, 35]
            ]
        }
    ]
}

# 用于生成唯一的标注ID
annotation_id = 1

# 遍历文件夹中的所有文件
for filename in os.listdir(annotation_path):
    if filename.endswith(".txt"):
        image_name = filename.replace(".txt", ".jpg")
        image_path = os.path.join(pic_path, image_name)
        txt_path = os.path.join(annotation_path, filename)

        # 读取图像尺寸
        with Image.open(image_path) as img:
            width, height = img.size

        # 添加图像信息到COCO
        image_id = len(coco_data["images"]) + 1
        coco_data["images"].append({
            "id": image_id,
            "width": width,
            "height": height,
            "file_name": image_name
        })

        # 解析YOLO格式的标注数据
        with open(txt_path, 'r') as file:
            for line in file.readlines():
                parts = line.strip().split()
                class_id = int(parts[0])
                x_center, y_center, bbox_width, bbox_height = map(float, parts[1:5])
                keypoints_relative = list(map(float, parts[5:]))  # 将map转换为list

                # 转换为COCO的边界框格式
                x_min = (x_center - bbox_width / 2) * width
                y_min = (y_center - bbox_height / 2) * height
                bbox_width_abs = bbox_width * width
                bbox_height_abs = bbox_height * height

                # 添加标注信息到COCO
                annotation = {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": 19,
                    "bbox": [x_min, y_min, bbox_width_abs, bbox_height_abs],
                    "area": bbox_width_abs * bbox_height_abs,
                    "segmentation": [],
                    "iscrowd": 0,
                    "isbbox": 1,
                    "keypoints": [],
                    "num_keypoints": 0
                }

                # 转换关键点坐标为绝对坐标并添加到关键点列表
                keypoints_absolute = []
                for i in range(0, len(keypoints_relative), 3):
                    kp_x = keypoints_relative[i] * width
                    kp_y = keypoints_relative[i + 1] * height
                    visibility = keypoints_relative[i + 2]  # 假设关键点是可见的
                    keypoints_absolute.extend([kp_x, kp_y, visibility])
                    annotation["num_keypoints"] += 1 if visibility > 0 else 0

                annotation["keypoints"] = keypoints_absolute

                coco_data["annotations"].append(annotation)
                annotation_id += 1

    # 保存COCO格式的数据到JSON文件
    with open('D:/WorkSapce/数据集转换/coco_output.json', 'w') as outfile:
        json.dump(coco_data, outfile, indent=4)