import json
import os


def convert_coco_to_yolo(json_file_path, output_dir, missing_data_file):
    # 加载 COCO 数据
    with open(json_file_path, 'r', encoding='utf-8') as file:
        coco_data = json.load(file)

    # 构建类别 ID 到名称的映射
    category_map = {category['id']: category['name'] for category in coco_data['categories']}

    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(missing_data_file, 'w', encoding='utf-8') as md_file:
        # 遍历所有图像
        for image in coco_data['images']:
            image_id = image['id']
            image_name = image['file_name'].replace('.jpg', '.txt')
            image_width = image['width']
            image_height = image['height']

            annotations = [ann for ann in coco_data['annotations'] if ann['image_id'] == image_id]

            with open(f"{output_dir}/{image_name}", 'w', encoding='utf-8') as file:
                for ann in annotations:
                    keypoints = ann.get('keypoints', [])
                    if len(keypoints) != 18 * 3:
                        # 记录缺失关键点数据的标注 ID
                        md_file.write(f"{ann['id']}\n")
                        continue  # 跳过此条标注

                    category_name = ann['metadata']['name']

                    bbox = ann['bbox']
                    x_center = (bbox[0] + bbox[2] / 2) / image_width
                    y_center = (bbox[1] + bbox[3] / 2) / image_height
                    bbox_width = bbox[2] / image_width
                    bbox_height = bbox[3] / image_height

                    # 写入标注数据，使用 Unicode 编码的类别名称
                    file.write(f"{category_name} {x_center} {y_center} {bbox_width} {bbox_height}")

                    # 处理关键点
                    for i in range(0, len(keypoints), 3):
                        kp_x = keypoints[i] / image_width
                        kp_y = keypoints[i + 1] / image_height
                        visibility = keypoints[i + 2]
                        file.write(f" {kp_x} {kp_y} {visibility}")

                    file.write("\n")


# 使用示例
json_file_path = 'coco-1710900748.9160733.json'  # JSON 文件的路径
output_directory = 'output_directory'  # 输出目录
missing_data_file = 'missing_data.txt'  # 缺失数据文件

convert_coco_to_yolo(json_file_path, output_directory, missing_data_file)


