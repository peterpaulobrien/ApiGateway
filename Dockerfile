# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: EPL-2.0
#
FROM frolvlad/alpine-python3

# Copy requirements.txt.
#COPY requirements.txt run.py /server/

RUN apk add --no-cache libstdc++ && \
    apk add --no-cache \
        --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community \
        lapack-dev && \
    apk add --no-cache \
        --virtual=.build-dependencies \
        gcc g++ gfortran musl-dev git \
        python3-dev && \
    ln -s locale.h /usr/include/xlocale.h && \
    pip install cython && \
    pip install flask && \
    pip install flask_api && \
    pip install pymongo && \
    pip install requests && \
    pip install waitress && \
    pip uninstall --yes cython && \
    rm /usr/include/xlocale.h && \
    rm -r /root/.cache && \
    apk del .build-dependencies

WORKDIR /src/app
ADD .. /src/app

# debug wrapper, followed by the model training script to execute
ENTRYPOINT [ "python", "api_gateway.py" ]

