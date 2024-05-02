import cv2
import os
import glob

def create_video(input_folder, output_video_path, fps=30):
    # Get all the png files in the directory
    image_files = sorted(glob.glob(os.path.join(input_folder, '*.png')))
    
    # Read the first image to obtain the size
    frame = cv2.imread(image_files[0])
    height, width, layers = frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can also use 'XVID'
    video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    # Add images to video
    for image_file in image_files:
        frame = cv2.imread(image_file)
        video.write(frame)  # Write the frame to the video

    # Release everything when job is finished
    video.release()
    print("Video created successfully!")

# Usage
input_folder = 'res/doom_frames_spinda'
output_video_path = 'output_video.mp4'
frames_per_second = 20  # Adjust to desired frames per second

create_video(input_folder, output_video_path, frames_per_second)