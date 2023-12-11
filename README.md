## Commands

- Set up environment
```shell
pipenv install
```

- Run server
```shell
cd server && pipenv run python server.py
```
From the repository's root directory

- Generate Python gRPC stubs
```shell
pipenv run python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. reddit.proto
```

- Run client
```shell
cd client && pipenv run python client.py
```
From the repository's root directory

- Run test
```shell
cd test && pipenv run python test.py
```
From the repository's root directory