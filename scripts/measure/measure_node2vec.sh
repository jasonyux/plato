#!/bin/bash

CUR_DIR=$(realpath $(dirname $0))
ROOT_DIR=$(realpath $CUR_DIR/../..)
cd $ROOT_DIR

INCSV=${INCSV:='twitter_cont'}
INPUT="hdfs://100.109.192.161:9000/user/plato/data/${INCSV}.csv"
OUTPUT="hdfs://100.109.192.161:9000/user/plato/${INCSV}_n2v"

# program config
IS_WEIGHTED=false
EPOCH=100
ALPHA=-1

# mpi related
WNUM=4
WCORES=4
ALL_HOSTS="9.67.166.117 100.109.192.161 100.109.188.177 9.66.174.10"

# env for JAVA && HADOOP
export LD_LIBRARY_PATH=${JAVA_HOME}/jre/lib/amd64/server:${LD_LIBRARY_PATH}

# env for hadoop
export CLASSPATH=${HADOOP_HOME}/etc/hadoop:`find ${HADOOP_HOME}/share/hadoop/ | awk '{path=path":"$0}END{print path}'`
export LD_LIBRARY_PATH="${HADOOP_HOME}/lib/native":${LD_LIBRARY_PATH}

run_n2v()
{
    MAIN="$ROOT_DIR/bazel-bin/example/node2vec_randomwalk" # process name

    export MPIRUN_CMD=${MPIRUN_CMD:="$ROOT_DIR/3rd/mpich/bin/mpiexec.hydra"}

    PARAMS+=" --threads ${WCORES}"
    PARAMS+=" --input ${INPUT} --output ${OUTPUT} --is_weighted=${IS_WEIGHTED}"
    PARAMS+=" --epoch ${EPOCH}"

    chmod 777 ${MAIN}
    ${MPIRUN_CMD} -n ${WNUM} -hosts ${HOSTS} ${MAIN} ${PARAMS}
}

grep_performance()
{
    echo $LOG_FILE
    cat $LOG_FILE | grep "random walk done"
}

config_hosts()
{
    local HOST_NUM=$1
    HOSTS=''
    for i in $ALL_HOSTS; do
        if [ $HOST_NUM -le 0 ]; then
            break
        fi
        HOSTS+=$i
        HOSTS+=","
        HOST_NUM=$((HOST_NUM-1))
    done
    HOSTS=${HOSTS::-1}
}

run_single()
{
    local HOST_NUM=$1
    config_hosts $HOST_NUM
    LOG_FILE="$ROOT_DIR/scripts/log/${INCSV}.n2v.${HOST_NUM}.${ITERATIONS}.log"
    run_n2v > $LOG_FILE 2>&1
    grep_performance
}

echo "[Performance]:"
run_single 1
run_single 2
run_single 3
run_single 4
