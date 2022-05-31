#!/usr/bin/env python3

from struct import pack
import numpy as np
import cv2 as cv
import mediapipe as mp

if __name__ == "__main__":
    mp_face_mesh = mp.solutions.face_mesh
    
    # Compute the mesh points.  One mesh per frame.
    meshes = []
    point_count = 0
    aspect_ratio = 1.0
    with mp_face_mesh.FaceMesh(
        static_image_mode=False, # Set false for video.
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5) as face_mesh:    

        i = 1
        cap = cv.VideoCapture("videos/BDGFACE 5_12.mp4")
        while cap.isOpened():
            print("\rReading frame", i, end = "")
            ret, image = cap.read()
            if not ret:
                break

            aspect_ratio = image.shape[1] / image.shape[0]
            results = face_mesh.process(cv.cvtColor(image, cv.COLOR_BGR2RGB))    
            if not results.multi_face_landmarks:
                meshes += [None]
            else:
                point_count = len(results.multi_face_landmarks[0].landmark)
                meshes += [results.multi_face_landmarks[0].landmark]
            
            i += 1
        cap.release()
    print("\rRead {} frames.                 ".format(len(meshes)))
    
    # Write the mdd file.
    fps = 24.0  # TODO: get this from the video file.
    frame_count = len(meshes)
    if frame_count > 0:
        with open("test.mdd", 'wb') as mdd:
            print("Vert count:", point_count)
        
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
    print()
            
