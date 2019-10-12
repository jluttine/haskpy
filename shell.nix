let
  #pkgs = import <nixpkgs> {};
  pkgs = import (builtins.fetchTarball {
    name = "nixos-unstable-2019-02-26";
    url = https://github.com/nixos/nixpkgs/archive/bc70e81b05474f630044a49fd31991aee71a2557.tar.gz;
    sha256 = "14wpw8sqxf130i07vc4x9a8dqfvp2sa61ic6896971ia7mmqs8sf";
  }) {};


  python = pkgs.python3Full;
  pythonPackages = pkgs.python3Packages;

in
pythonPackages.buildPythonPackage rec {
  name = "haskpy";
  doCheck = false;
  src = ./.;
  depsBuildBuild = with pythonPackages; [
    ipython
    pytest
    pip
    versioneer
  ];
  buildInputs = with pythonPackages; [
    attrs
    toolz
  ];
}
