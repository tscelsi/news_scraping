aws ecr get-login-password --profile tlscelsi-student --region ap-southeast-2 | docker login --username AWS --password-stdin 195351931411.dkr.ecr.ap-southeast-2.amazonaws.com
docker build -t news-scraping-repository .
docker tag news-scraping-repository:latest 195351931411.dkr.ecr.ap-southeast-2.amazonaws.com/news-scraping-repository:latest
docker push 195351931411.dkr.ecr.ap-southeast-2.amazonaws.com/news-scraping-repository:latest