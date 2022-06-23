# Face Track

A very simple Python script that uses a not-at-all simple Python library to generate animated face meshes from video files.

Basic usage:

```bash
$ face_track.py path/to/video_file.mp4 path/to/output.mdd
```

This will create `output.mdd`, a NewTek MDD file.  This file contains animated vertex data, which can be used to animate the face mesh in `face_mesh.obj` or `face_mesh.blend`.  For example, by using the Mesh Cache modifier in Blender.


## Accounting for Perspective

By default, this script just spits out the direct results of Google's Mediapipe library.  Those results assume an orthographic camera, meaning that as the face gets closer/further away from the camera, the resulting face mesh actually gets bigger/smaller rather than adjusting its z-depth.

To get a face mesh that (more or less) accounts for perspective, you can specify the camera's field of view.  The script will then process the face mesh data to be consistent with that.  (Note that this does not produce perfect results by any stretch, but it may be workable for certain use cases at least.)

You can specify the field of view in one of two ways.  Either in (horizontal) degrees:

```bash
$ face_track.py --fov 85 path/to/video_file.mp4 path/to/output.mdd
```

Or with a sensor-size/lens-length pair:

```bash
$ face_track.py --lens_len 35/50 path/to/video_file.mp4 path/to/output.mdd
```

Both options are designed to match the perspective camera model in Blender, and using the exact same camera settings should result in perfect alignment with that camera.

A separate blend file, `face_mesh_perspective.blend`, is provided with the basic setup for a perspective-corrected face mesh generated this way.


## Requirements

face_track.py requires the following:

- [Python 3](https://www.python.org)
- [Numpy](https://numpy.org)
- [OpenCV](https://opencv.org) and its Python bindings
- [Mediapipe](https://mediapipe.dev) and its Python bindings


## Support

This project is a quick hack held together by ducttape and glue, and is 100% unsupported.  Issue reports and contributions are welcome, but we make no promises they will be acted upon.

If you would like to further develop this, we recommend forking it into a new project.


## License

All files in this project are licensed under [CC0](https://creativecommons.org/publicdomain/zero/1.0/).  Please see LICENSE.md for details.
