import os

def correct_keypoints_in_file(input_file_path, output_file_path):
    # 读取原始数据
    with open(input_file_path, 'r') as infile:
        lines = infile.readlines()

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    # 修正关键点数据并写入新文件
    with open(output_file_path, 'w') as outfile:
        for line in lines:
            parts = line.split()
            if len(parts) < 5:
                outfile.write(line)
                continue

            # 写入类别和边界框数据
            outfile.write(' '.join(parts[:5]) + ' ')

            # 修正关键点
            for i in range(5, len(parts), 3):
                if i + 2 < len(parts):
                    x, y = max(float(parts[i]), 0), max(float(parts[i + 1]), 0)
                    confidence = float(parts[i + 2])
                    # 如果x和y原始坐标为0，则置信度设为0，否则保持原始置信度
                    confidence = 0 if x == 0 and y == 0 else confidence
                    outfile.write(f"{x} {y} {confidence} ")
            outfile.write('\n')

def correct_keypoints_in_directory(input_directory, output_directory):
    # 遍历指定文件夹中的所有.txt文件
    for filename in os.listdir(input_directory):
        if filename.endswith('.txt'):
            input_file_path = os.path.join(input_directory, filename)
            output_file_path = os.path.join(output_directory, filename)
            correct_keypoints_in_file(input_file_path, output_file_path)
            print(f"Processed {filename}")

# 输入和输出文件夹路径
input_directory = 'D://WorkSapce//guowang//dataset2//labels//val'  # 替换为实际的输入文件夹路径
output_directory = 'D://WorkSapce//guowang//dataset2//labels//val1'  # 替换为实际的输出文件夹路径

correct_keypoints_in_directory(input_directory, output_directory)
