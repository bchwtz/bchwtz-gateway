#!/bin/bash
go install github.com/princjef/gomarkdoc/cmd/gomarkdoc@latest

gomarkdoc --output ../docs/go-services/cli_ref.md ./cmd/cli
gomarkdoc --output ../docs/go-services/dumper_ref.md ./cmd/dumper
gomarkdoc --output ../docs/go-services/gateway_ref.md ./internal/gateway
gomarkdoc --output ../docs/go-services/model_ref.md ./internal/model
gomarkdoc --output ../docs/go-services/commandinterface_ref.md ./internal/commandinterface
