docker build -t biocad-siz:1.0 .

docker run \
--name app1 \
-v /Users/chertan/PycharmProjects/sirius_23_siz:/app \
-p 8000:8000 \
-e ENV_VAR=333 \
biocad-siz:1.0