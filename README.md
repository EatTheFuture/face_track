# Face Track

A very simple Python script that uses a not-at-all simple Python library to generate animated face meshes from video files.

Basic usage:

```bash
$ face_track.py path/to/video_file.mp4 path/to/output.mdd
```

This will create `output.mdd`, a NewTek MDD file.  This file contains animated vertex data, which can be used to animate the face mesh in `face_mesh.obj` or `face_mesh.blend`.  For example, by using the Mesh Cache modifier in Blender.


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
