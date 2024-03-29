#!/bin/bash
export SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo $SCRIPT_DIR
export PROTOC_OUTDIR=$SCRIPT_DIR/../proto_generated
mkdir -p $PROTOC_OUTDIR
echo $PROTOC_OUTDIR
cd $SCRIPT_DIR
python3 -m grpc_tools.protoc -I . --python_out $PROTOC_OUTDIR --purerpc_out $PROTOC_OUTDIR *.proto
sed -i $PROTOC_OUTDIR/*.py -e 's/^import [^ ]*_pb2/from . \0/'
