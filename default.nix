let
  pkgs = import <nixpkgs> { };
  # pkgs = import (builtins.fetchTarball {
  #   name = "nixos-unstable-2019-02-26";
  #   url = https://github.com/nixos/nixpkgs/archive/bc70e81b05474f630044a49fd31991aee71a2557.tar.gz;
  #   sha256 = "14wpw8sqxf130i07vc4x9a8dqfvp2sa61ic6896971ia7mmqs8sf";
  # }) {};

  ps = pkgs.python3Packages;

in
ps.buildPythonPackage rec {
  name = "haskpy";
  doCheck = false;
  src = ./.;
  postShellHook = ''
    export PYTHONPATH=$(pwd):$PYTHONPATH
  '';
  depsBuildBuild = with ps; [
    ipython
    pytest
    pip
    twine
    sphinx
    setuptools_scm
    pkgs.git
  ];
  propagatedBuildInputs = with ps; [
    attrs
    hypothesis
    toolz
    cytoolz
    importlib-metadata
    numpydoc
  ];

}
