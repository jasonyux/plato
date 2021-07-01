#!/bin/bash

CUR_DIR=$(realpath $(dirname $0))
ROOT_DIR=$(realpath $CUR_DIR/..)
cd $ROOT_DIR

MAIN="$ROOT_DIR/bazel-bin/example/pagerank" # process name

WNUM=4
WCORES=4

INPUT=${INPUT:='hdfs://100.109.192.161:9000/user/plato/data/v100_e2150_ua_c3.csv'}
OUTPUT=${OUTPUT:='hdfs://100.109.192.161:9000/user/plato/v100_e2150_ua_c3'}
NOT_ADD_REVERSED_EDGE=${NOT_ADD_REVERSED_EDGE:=true}  # let plato auto add reversed edge or not

ALPHA=-1
PART_BY_IN=false

EPS=${EPS:=0.0001}
DAMPING=${DAMPING:=0.85}
ITERATIONS=${ITERATIONS:=100}

export MPIRUN_CMD=${MPIRUN_CMD:="$ROOT_DIR/3rd/mpich/bin/mpiexec.hydra"}

PARAMS+=" --threads ${WCORES}"
PARAMS+=" --input ${INPUT} --output ${OUTPUT} --is_directed=${NOT_ADD_REVERSED_EDGE}"
PARAMS+=" --iterations ${ITERATIONS} --eps ${EPS} --damping ${DAMPING}"

# env for JAVA && HADOOP
export LD_LIBRARY_PATH=${JAVA_HOME}/jre/lib/amd64/server:${LD_LIBRARY_PATH}

# env for hadoop
export CLASSPATH=${HADOOP_HOME}/etc/hadoop:`find ${HADOOP_HOME}/share/hadoop/ | awk '{path=path":"$0}END{print path}'`
export LD_LIBRARY_PATH="${HADOOP_HOME}/lib/native":${LD_LIBRARY_PATH}

HOSTS="$ROOT_DIR/scripts/hosts" # hostfile with ips

chmod 777 ${MAIN}
${MPIRUN_CMD} -n ${WNUM} -f ${HOSTS} ${MAIN} ${PARAMS}
exit $?