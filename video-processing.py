import os
import cv2
from scenedetect import VideoManager
from scenedetect import SceneManager
from scenedetect.detectors import ContentDetector

def find_scenes(video_path, threshold=27.0):
    # Create our video & scene managers, then add the detector.
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold)) # (delta_hue, delta_sat, delta_lum, delta_edges) = 1.0 0.5 1.0 0.2

    # Start our video manager.
    video_manager.start()

    # Perform scene detection on video_manager.
    scene_manager.detect_scenes(frame_source=video_manager)

    # Obtain list of detected scenes.
    scene_list = scene_manager.get_scene_list()

    # We only need the video_manager for its duration so far, so close it.
    video_manager.release()

    return scene_list

def save_frames(video_path, scenes, output_dir='output_frames'):

    scene_times = []

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video: {video_path}")
        return

    for i, scene in enumerate(scenes):
        start_frame = scene[0].frame_num
        start_time = scene[0].get_seconds()
        scene_times.append(start_time)
        # Format the start time as h-m-s-ms
        start_time_formatted = '{:02d}-{:02d}-{:02d}-{:03d}'.format(
            int(start_time // 3600),
            int((start_time % 3600) // 60),
            int(start_time % 60),
            int((start_time * 1000) % 1000)
        )

        # Seek to the start frame.
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        ret_val, frame = cap.read()
        if ret_val:
            # Include the start time in the filename
            output_file_path = os.path.join(output_dir, f"scene_{i+1}_start-{start_time_formatted}.jpg")
            cv2.imwrite(output_file_path, frame)

    cap.release()
    return scene_times
    

video_path = 'data/Episode01.avi'
scenes = find_scenes(video_path)
scene_times = save_frames(video_path, scenes)

# Print or process the scene times
for i, start_time in enumerate(scene_times):
    print(f"Scene {i+1}: Start - {start_time:.3f}s")