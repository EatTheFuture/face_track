let
    # You can replace "unstable" with any channel name to use that channel.
    pkgs = import <unstable> {};
    pypkgs = pkgs.python310Packages;
    name = "face_track_dev_env";
in pkgs.stdenv.mkDerivation {
    inherit name;
    nativeBuildInputs = with pkgs; [
        pypkgs.python
        pypkgs.pip
        pypkgs.numpy
        pypkgs.opencv4
        pypkgs.dlib
    ];

    shellHook = with pkgs; ''
        export PYTHON_LIBRARY="${pypkgs.python.libPrefix}"
        export PYTHON_LIBPATH="${pypkgs.python}/lib"
        export PYTHON_INCLUDE_DIR="${pypkgs.python}/include/${pypkgs.python.libPrefix}"
        export PYTHON_VERSION="${pypkgs.python.pythonVersion}"
        export PYTHON_NUMPY_PATH="${pypkgs.numpy}/${pypkgs.python.sitePackages}"
        export PYTHON_NUMPY_INCLUDE_DIRS="${pypkgs.numpy}/${pypkgs.python.sitePackages}/numpy/core/include"
        export PYTHONPATH="$PYTHONPATH:$HOME/.local/lib/python3.10/site-packages"
        export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python      
    '';
}
