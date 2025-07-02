import json
import av
import cv2
import webvtt
import os
import subprocess

def time_to_seconds(time_str):
    hours, minutes, seconds = time_str.split(':')
    seconds, milliseconds = seconds.split('.')
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000.0
    return total_seconds

def get_segments_from_subtitles(subtitle_file, video_duration):
    segments = []
    for caption in webvtt.read(subtitle_file):
        start_time = time_to_seconds(caption.start)
        end_time = time_to_seconds(caption.end)
        segments.append((start_time, end_time))
    if not segments:
        return [(0, video_duration)]
    return segments

def process_video_segment(container, video_stream, fps, start_time, end_time, segment_index, output_folder, key_frame_data):
    fgbg = cv2.createBackgroundSubtractorMOG2()
    threshold = 10000
    key_frame_indices = []

    container.seek(int(start_time * av.time_base))
    frame_idx = 0

    for frame in container.decode(video_stream):
        timestamp = frame.time
        if start_time <= timestamp <= end_time:
            frame_image = frame.to_ndarray(format='bgr24')
            fgmask = fgbg.apply(frame_image)
            _, thresh = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
            non_zero_count = cv2.countNonZero(thresh)
            if non_zero_count > threshold:
                key_frame_indices.append(frame_idx)
            frame_idx += 1

    n = 2
    final_key_frame_indices = []
    start_idx = key_frame_indices[0] if key_frame_indices else None
    for i in range(1, len(key_frame_indices)):
        current_idx = key_frame_indices[i]
        prev_idx = key_frame_indices[i - 1]
        if current_idx - prev_idx > n:
            if start_idx is not None:
                final_key_frame_indices.append(start_idx)
                if prev_idx != start_idx:
                    final_key_frame_indices.append(prev_idx)
                else:
                    final_key_frame_indices.append(start_idx)
            start_idx = current_idx
    if start_idx is not None:
        final_key_frame_indices.append(start_idx)
        if key_frame_indices[-1] != start_idx:
            final_key_frame_indices.append(key_frame_indices[-1])
        else:
            final_key_frame_indices.append(start_idx)
            
    i = 0
    if final_key_frame_indices:
        if start_time < (start_time + final_key_frame_indices[0] / fps):
            key_frame_data[(segment_index, 0)] = (start_time, start_time + final_key_frame_indices[0] / fps)
        i += 1
        while i < len(final_key_frame_indices) - 1:
            start_idx = final_key_frame_indices[i]
            end_idx = final_key_frame_indices[i + 1]
            key_frame_data[(segment_index, i // 2 + 1)] = (start_idx / fps + start_time, end_idx / fps + start_time)
            i += 2
        if i < len(final_key_frame_indices) and (final_key_frame_indices[-1] / fps + start_time) < end_time:
            key_frame_data[(segment_index, i // 2 + 1)] = (final_key_frame_indices[-1] / fps + start_time, end_time)
    else:
        if start_time < end_time:
            key_frame_data[(segment_index, 0)] = (start_time, end_time)

def cut_video(video_path, start_time, end_time, output_path):
    command = [
        'ffmpeg',
        '-ss', str(start_time),
        '-i', video_path,
        '-vframes', '1',
        output_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def process_video(video_path, subtitle_file, output_folder, output_folder_v):
    json_filename = os.path.join(output_folder, f"key_frame.json")
    if not os.path.exists(json_filename):
        container = av.open(video_path)
        video_duration = container.duration / av.time_base
        if video_duration > 600:
            container.close()
            return
        segments = get_segments_from_subtitles(subtitle_file, video_duration)
        os.makedirs(output_folder, exist_ok=True)
        video_stream = next(s for s in container.streams if s.type == 'video')
        fps = video_stream.average_rate
        key_frame_data = {}
        for segment_index, (start_time, end_time) in enumerate(segments):
            if segment_index < len(segments) - 1:
                end_time = segments[segment_index+1][0]
            else:
                end_time = video_duration
            process_video_segment(container, video_stream, fps, start_time, end_time, segment_index + 1, output_folder, key_frame_data)
        container.close()
        with open(json_filename, "w", encoding="utf-8") as json_file:
            json.dump({str(k): v for k, v in key_frame_data.items()}, json_file, ensure_ascii=False, indent=4)
    else:
        with open(json_filename, "r", encoding="utf-8") as json_file:
            key_frame_data = json.load(json_file)
        key_frame_data = {eval(k): v for k, v in key_frame_data.items()}
    sorted_keys = sorted(key_frame_data.keys(), key=lambda x: x[0])
    for i, keyframe_key in enumerate(sorted_keys):
        segment_index, key_frame_index = keyframe_key
        segment_output_path = os.path.join(output_folder_v, f"segment_{segment_index}_{key_frame_index}.png")
        if os.path.exists(segment_output_path):
            continue
        start_time = key_frame_data[keyframe_key][0]
        end_time = key_frame_data[keyframe_key][1]
        if start_time >= video_duration:
            break
        if end_time > video_duration:
            end_time = video_duration
        cut_video(video_path, start_time, end_time, segment_output_path)

def get_subtitle_video_pairs(subtitle_base_path, video_base_path):
    pairs = []
    for root, dirs, files in os.walk(subtitle_base_path):
        for file in files:
            if file.endswith('.vtt'):
                subtitle_file = os.path.join(root, file)
                relative_path = os.path.relpath(root, subtitle_base_path)
                video_folder = os.path.join(video_base_path, relative_path)
                video_name = file.replace('.vtt', '.mp4')
                video_file = os.path.join(video_folder, video_name)
                if os.path.exists(video_file):
                    pairs.append((subtitle_file, video_file))
    return pairs

def process_all_videos_and_subtitles(subtitle_base_path, video_base_path, output_base_path):
    pairs = get_subtitle_video_pairs(subtitle_base_path, video_base_path)
    for subtitle_file, video_file in pairs:
        relative_path = os.path.relpath(video_file, video_base_path)
        output_folder = os.path.join(output_base_path, os.path.dirname(relative_path), os.path.basename(video_file).replace('.mp4', ''))
        os.makedirs(output_folder, exist_ok=True)
        process_video(video_file, subtitle_file, output_folder)

if __name__ == "__main__":
    app = "word"
    subtitle_base_path = f'audios_text/{app}'
    video_base_path = f'videos/{app}'
    output_base_path = f'images/{app}'
    process_all_videos_and_subtitles(subtitle_base_path, video_base_path, output_base_path)
