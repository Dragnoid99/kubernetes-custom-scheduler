#!/bin/bash

cd locust01
./script.sh
cd ..

cd locust02
./script.sh
cd ..

cd locust11
./script.sh
cd ..

cd locust12
./script.sh
cd ..

cd locust13
./script.sh
cd ..

cd locust21
./script.sh
cd ..

cd locust22
./script.sh
cd ..

cd locust23
./script.sh
cd ..

cd locust24
./script.sh
cd ..

cd locust25
./script.sh
cd ..

docker run -itd --net host locust-0-1

docker run -itd --net host locust-0-2

docker run -itd --net host locust-1-1

docker run -itd --net host locust-1-2

docker run -itd --net host locust-1-3

docker run -itd --net host locust-2-1

docker run -itd --net host locust-2-2

docker run -itd --net host locust-2-3

docker run -itd --net host locust-2-4

docker run -itd --net host locust-2-5

