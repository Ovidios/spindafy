import cv2
import os

def extract_frames(video_path, output_folder, frame_rate):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Capture video from file
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = video.get(cv2.CAP_PROP_FPS)
    
    # Calculate interval between frames to capture based on the desired frame rate
    frame_interval = video_fps / frame_rate

    current_frame = 0
    saved_frame = 0

    while True:
        # Set video position
        video.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        success, frame = video.read()
        
        if not success:
            break  # Break if no frame is found (end of video)

        # Save frame as PNG file
        output_filename = os.path.join(output_folder, f"frame_{saved_frame:04d}.png")
        cv2.imwrite(output_filename, frame)
        print(f"Saved {output_filename}")

        saved_frame += 1
        current_frame += frame_interval

    # Release video capture object
    video.release()
    print("Finished extracting frames.")

# Usage example:
video_path = 'res/converted_video.mp4'
output_folder = 'res/'
frame_rate = 20  # Extract 20

extract_frames(video_path, output_folder, frame_rate)