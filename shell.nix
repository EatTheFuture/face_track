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
        export PYTHONPATH="$PYTHONPATH:$HOME/.local/lib/python3.10/site-packages"
        export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
    '';
}
