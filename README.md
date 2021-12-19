# Create Requirements File

## Installation
```sh
$ sh install.sh
```

## Usage
```sh
$ genreq --help

usage: genreq [-h] [-p PATH] [-s {>=,==,~=}] [-nv]

Create a requirements.txt file from a project directory

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to the project directory
  -s {>=,==,~=}, --specifier {>=,==,~=}
                        Version specifier
  -nv, --no-version     Appends package name without its version
```

## Examples
```sh
$ genreq -p "/path/to/my/project"
$ genreq -p "/path/to/my/project" -s "~="
$ genreq -p "/path/to/my/project" -nv
```
