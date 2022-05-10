# dtpln-lambda-name
intro here

## Prerequisites

- Use an IDE with syntax highlighting
- Have the newest version of Docker on your HOST machine
- Ideally you are working on a *nix based system

## Parameters

- Lambda module and handler is default `lambda_function.lambda_handler`
- Required libraries and modules are described in `requirements.txt`

## How setup the environment on your host machine (Local Dev)

You should create an `.env` file (simply base it off of `.env.example`) in the root of this repository with the corresponding values. 

Afterwards, you need to install the modules and dependencies from the `requirements.txt` file. For this, we utilize Python's virtual environment and the build flavor of the Docker image from lambci/lambda to download and build everything on the `v-env` subfolder:

```
docker run --rm -v $(pwd)/src:/var/task lambci/lambda:build-python3.7 sh -c "python3 -m venv v-env && source v-env/bin/activate && pip install -r requirements.txt"
```

After that you should be able to a `v-env` subfolder in /src

## How to execute Tests

1. From the root of this repository run `docker-compose -f docker-compose.test.yml run lambda-name-start_dependencies` to start the mock servers for S3 and for DynamoDB and the dtpln-cs-intg in its mock lambda environment
2. After the dependencies are running issue the following command: `docker-compose -f docker-compose.test.yml run lambda-name-seeder` to seed the S3 server with some data
4. Finally, run `docker-compose -f docker-compose.test.yml run dtpln-lambda-name-test`
5. Test results should appear on your terminal screen

References:

- https://github.com/lambci/docker-lambda
- https://docs.aws.amazon.com/lambda/latest/dg/python-package.html

## How to Build and Package the Lambda

1. From the root of this repository run `docker build -f ./Dockerfile.build -t dtpln-lambda-name:build .`
2. After the image has been built, run: `docker run -v $(pwd)/dist:/tmp dtpln-lambda-name:build`
3. You should now have a `/dist` folder with the `.zip` file inside it

## How to Deploy the Lambda

1. Use AWS CLI with your credentials to update the lambda function or simply login to the AWS console and drop it there
2. All relevant environment variables specified in the `.env` need to be defined again via the AWS console on the specific Lambda

