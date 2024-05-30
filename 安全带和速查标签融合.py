import os
import glob


def parse_annotation(file_path):
    if os.path.getsize(file_path) == 0:  # Check if the file is empty
        return [0.0, 0.0, 0.0, 0.0], ['0.000000'] * 18 * 3  # Return empty bbox and 18 keypoints filled with zeros
    with open(file_path, 'r') as file:
        data = file.read().strip().split(' ')
        bbox = [float(data[1]), float(data[2]), float(data[3]), float(data[4])]  # x, y, width, height
        keypoints = data[5:]
    return bbox, keypoints


def merge_data(safety_belt_data, human_data):
    safety_belt_bbox, safety_belt_keypoints = safety_belt_data
    human_bbox, human_keypoints = human_data
    # Merge with safety belt bbox and keypoints first, then human keypoints
    merged_data = ['0'] + list(map(str, safety_belt_bbox)) + safety_belt_keypoints + human_keypoints
    return ' '.join(merged_data)


def process_files(human_dir, safety_belt_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for safety_belt_file in glob.glob(os.path.join(safety_belt_dir, '*.txt')):
        file_id = os.path.basename(safety_belt_file).split('.')[0]
        human_file = os.path.join(human_dir, file_id + '.txt')

        safety_belt_bbox, safety_belt_keypoints = parse_annotation(safety_belt_file)
        if os.path.exists(human_file) and os.path.getsize(human_file) > 0:
            human_bbox, human_keypoints = parse_annotation(human_file)
        else:
            # If there is no human file or it's empty, fill with zeros
            human_bbox = [0.0, 0.0, 0.0, 0.0]
            human_keypoints = ['0.000000'] * 17 * 3  # Assuming 17 human keypoints each with 3 values

        merged_data = merge_data((safety_belt_bbox, safety_belt_keypoints), (human_bbox, human_keypoints))

        with open(os.path.join(output_dir, file_id + '.txt'), 'w') as out_file:
            out_file.write(merged_data)


process_files('human', 'safetyBelt', 'merged_dataset')
