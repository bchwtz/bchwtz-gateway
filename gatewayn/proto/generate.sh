#!/bin/bash
export SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo $SCRIPT_DIR
export PROTOC_OUTDIR=$SCRIPT_DIR/../proto_generated
echo $PROTOC_OUTDIR
cd $SCRIPT_DIR
python3 -m grpc_tools.protoc -I . --python_out $PROTOC_OUTDIR --grpc_python_out $PROTOC_OUTDIR *.proto
sed -i $PROTOC_OUTDIR/*_pb2.py -e 's/^import [^ ]*_pb2/from . \0/'
