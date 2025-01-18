# docker-autotrace

Run [`autotrace`](https://github.com/autotrace/autotrace) (the bitmap-to-vector-graphics converter) from Docker.

**Note:** This project has no affiliation with the `autotrace` project. `docker-autotrace` is merely a convenience tool.

Installing `autotrace` can be a bit of a hassle on some systems, so this repository makes the installation as easy as running 2 or 3 commands. (Assuming `git` and [`docker`](https://docs.docker.com/get-docker/) is already installed)

# Installation

1. Clone this repository.
2. In the cloned repository, run `docker build -t autotrace -f Dockerfile .`, or alternatively, `make build`. This may take a few minutes.

This will create an image called `autotrace` that you can invoke from Docker.

```
docker run --rm -t -v "$PWD:$PWD" -w "$PWD" autotrace [YOUR ARGUMENTS HERE]
```

## Installing it "globally"

To use `autotrace` globally on your system, run the following command in your shell or add it to your shell configuration file.

```
alias autotrace='docker run --rm -v "$PWD:$PWD" -w "$PWD" autotrace'
```

Now you can invoke `autotrace` from anywhere.

```
% autotrace
Usage: /autotrace/.libs/autotrace [options] <image_file_name>
(Missing <image_name>.)
For more information, use ''-help''.
```

**Note:** You won't be able to run `autotrace` on files outside of the directory you are in (i.e. `../` won't work). Only files in the current directory or sub-directory can be referenced. If such functionality is needed, try out the [`shim/autotrace`](shim/autotrace) script, which can be copied into `/usr/local/bin` (or use `make install-shim`).

# Example and Demo

Using the alias, this is as easy as:

```
autotrace -centerline -color-count 2 example-input.png -output-file example-output.svg -output-format svg -corner-threshold 150 -background-color FFFFFF
```

Running the command should result in the example input being transformed into a traced stroke lines.

| Before | After |
|--------|-------|
| ![An image of the bitmap example.](example-input.png) | ![An image of the bitmap example, converted to an SVG file.](example-output.svg) |
