#!/usr/bin/env python3

import argparse
import math
from struct import pack
import numpy as np
import cv2 as cv
import mediapipe as mp


eye_l_idxs = [474, 475, 476, 477]
eye_r_idxs = [469, 470, 471, 472]
head_idxs = [34, 264]

# For averaging depth estimate out over multiple frames.
WINDOW_WIDTH = 3


def distance(a, b):
    x = a.x - b.x
    y = a.y - b.y
    z = a.z - b.z

    return ((x * x) + (y * y) + (z * z))**0.5


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description=
        """
        Processes video of a human face into 3D face mesh animation
        data.  Currently only supports video files with a single face.
        """
    )
    arg_parser.add_argument("--fov", help="Attempt to account for perspective projection based on the given horizontal fov (in degrees).")
    arg_parser.add_argument("--focal_len", help="Same as --fov except it takes sensor size / focal length (e.g. \"35/60\" for a 35mm sensor and 60mm lens).")
    arg_parser.add_argument("input_video", help="The input video file with a person's face in it.")
    arg_parser.add_argument("output_mdd", help="The .mdd file to write the mesh animation data to.")
    args = arg_parser.parse_args()

    video_path = args.input_video
    mdd_path = args.output_mdd
    camera_scale = None
    if args.fov is not None:
        try:
            fov = float(args.fov)
            camera_scale = 2.0 * math.tan(math.radians(fov / 2))
        except:
            print("Error: the specified fov, '{}', is not a number.".format(args.fov))
            exit()
    elif args.focal_len is not None:
        error_msg = "Error: focal_len must be specified as two numbers separated by a slash (no spaces).  E.g. \"35/60\" for a 35mm sensor and 60mm lens."
        try:
            sensor_lens = args.focal_len.split("/")
            if len(sensor_lens) != 2:
                raise None
            sensor = float(sensor_lens[0])
            lens = float(sensor_lens[1])
            camera_scale = sensor / lens
        except:
            print(error_msg)
            exit()



    #----------------------------------------------------------
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


    #----------------------------------------------------------
    # Compute distance and average Z coordinate of our metric head width
    # vertices for each frame.
    width_2d_and_z = []
    for mesh in meshes:
        if mesh is None:
            width_2d_and_z += [None]
        else:
            d = distance(mesh[head_idxs[0]], mesh[head_idxs[1]])
            z = (mesh[head_idxs[0]].z + mesh[head_idxs[1]].z) * 0.5
            width_2d_and_z += [(d, z)]


    #----------------------------------------------------------
    # Write the mdd file.
    frame_count = len(meshes)
    if frame_count > 0:
        with open(mdd_path, 'wb') as mdd:

            mdd.write(pack(">2i", frame_count, point_count))
            mdd.write(pack(">%df" % (frame_count), *[frame / fps for frame in range(frame_count)]))

            for mesh, i in zip(meshes, range(len(meshes))):
                print("\rWriting frame", i, end = "")
                if mesh is None:
                    # Put all vertices at the origin for bogus frames.
                    for n in range(point_count):
                        mdd.write(pack(">3f", 0.0, 0.0, 0.0))
                elif camera_scale is None:
                    # No camera fov, so just do simple orthographic.
                    for point in mesh:
                        x = point.x - 0.5
                        y = point.y - 0.5
                        mdd.write(pack(">3f", x, -y / aspect_ratio, -point.z))
                else:
                    # Compute a rolling average of width_2d_and_z.
                    w2d = width_2d_and_z[i][0]
                    wz = width_2d_and_z[i][1]
                    k = 1
                    for j in range(1, WINDOW_WIDTH + 1):
                        if (i + j) < len(width_2d_and_z):
                            w2d_z = width_2d_and_z[i + j]
                            if w2d_z is None:
                                break
                            w2d += w2d_z[0]
                            wz += w2d_z[1]
                            k += 1
                    for j in range(1, WINDOW_WIDTH + 1):
                        if (i - j) >= 0:
                            w2d_z = width_2d_and_z[i - j]
                            if w2d_z is None:
                                break
                            w2d += w2d_z[0]
                            wz += w2d_z[1]
                            k += 1
                    w2d /= k
                    wz /= k

                    # Compute and write out mesh coordinates.
                    scale = 1.0 / w2d
                    for point in mesh:
                        z = ((point.z - wz) * camera_scale * scale) + scale
                        x = (point.x - 0.5) * camera_scale * z
                        y = ((point.y - 0.5) * camera_scale / aspect_ratio) * z

                        mdd.write(pack(
                            ">3f",
                            x / camera_scale,
                            -y / camera_scale,
                            -z / camera_scale,
                        ))

    print("\rWrote {} frames.                 ".format(len(meshes)))


