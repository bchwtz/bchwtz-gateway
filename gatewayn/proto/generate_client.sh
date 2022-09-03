#!/bin/bash
go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.28
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.2
protoc -I ./ --go_out ../../client/generated --go-grpc_out ../../client/generated --go_opt=paths=source_relative --go-grpc_opt=paths=source_relative *.proto