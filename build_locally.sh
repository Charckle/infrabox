USERNAME=charckle
#VERSION=$(cat VERSION)
IMAGE=infrabox

docker build -f Dockerfile -t $USERNAME/$IMAGE:latest .
