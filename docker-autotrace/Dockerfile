FROM debian:stable-20230522-slim

# 1. Fetch new versions of packages.
# 2. Fetch `git`, so we can download the `autotrace` source.
# 3. Fetch `build-essentials`, so we can use `Make`.
# 4. Fetch `autotrace` dependencies (See `autotrace`'s GitHub action), without unnecessary dependencies (`--no-install-recommends`).
# 5. Clean and remove package manager cache.
RUN apt-get update \
 && apt-get -y install git \
 && apt-get -y install build-essential \
 && apt-get -y install libgraphicsmagick1-dev libpng-dev libexiv2-dev libtiff-dev libjpeg-dev libxml2-dev libbz2-dev libfreetype6-dev libpstoedit-dev autoconf automake libtool intltool autopoint --no-install-recommends \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 1. Download `autotrace` source code. (Just the latest files in the default branch)
# 2. Change directory. (This puts us in the directory `/autotrace`)
# 3. Follow the instructions in `autotrace`'s GitHub action.
# 4. Finally, run the check to confirm everything was properly installed.
RUN git clone --depth 1 https://github.com/autotrace/autotrace.git \
 && cd autotrace \
 && ./autogen.sh \
 && ./configure \
 && make \
 && make check

ENTRYPOINT ["/autotrace/autotrace"]
