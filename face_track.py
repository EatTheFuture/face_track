#!/usr/bin/env python3

import argparse
from struct import pack
import numpy as np
import cv2 as cv
import mediapipe as mp

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description=
        """
        Processes video of a human face into 3D face mesh animation
        data.  Currently only supports video files with a single face.
        """
    )
    arg_parser.add_argument("input_video", help="The input video file with a person's face in it.")
    arg_parser.add_argument("output_mdd", help="The .mdd file to write the mesh animation data to.")
    args = arg_parser.parse_args()

    video_path = args.input_video
    mdd_path = args.output_mdd

    # Compute the mesh points from the input video.
    meshes = []  # One mesh per frame.
    point_count = 0
    width = 0
    height = 0
    fps = 0
    aspect_ratio = 1.0
    with mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False, # Set false for video.
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5) as face_mesh:

        video = cv.VideoCapture(video_path)

        width = video.get(cv.CAP_PROP_FRAME_WIDTH)
        height = video.get(cv.CAP_PROP_FRAME_HEIGHT)
        fps = video.get(cv.CAP_PROP_FPS)
        aspect_ratio = width / height
        print("Input video fps: {}".format(fps))
        print("Input video resolution: {}x{}".format(int(width), int(height)))

        i = 1
        while video.isOpened():
            ret, image = video.read()
            print("\rReading frame", i, end = "")
            if not ret:
                break

            results = face_mesh.process(cv.cvtColor(image, cv.COLOR_BGR2RGB))
            if not results.multi_face_landmarks:
                meshes += [None]
            else:
                point_count = len(results.multi_face_landmarks[0].landmark)
                meshes += [results.multi_face_landmarks[0].landmark]

            i += 1
        video.release()
    print("\rRead {} frames.                 ".format(len(meshes)))
    print("Generated vert count:", point_count)

    # Write the mdd file.
    frame_count = len(meshes)
    if frame_count > 0:
        with open(mdd_path, 'wb') as mdd:

            mdd.write(pack(">2i", frame_count, point_count))
            mdd.write(pack(">%df" % (frame_count), *[frame / fps for frame in range(frame_count)]))

            i = 1
            for mesh in meshes:
                print("\rWriting frame", i, end = "")
                if mesh is None:
                    # Put all vertices at the origin for bogus frames.
                    for n in range(point_count):
                        mdd.write(pack(">3f", 0.0, 0.0, 0.0))
                else:
                    for point in mesh:
                        mdd.write(pack(">3f", point.x, point.y / aspect_ratio, point.z))
                i += 1

    print("\rWrote {} frames.                 ".format(len(meshes)))
