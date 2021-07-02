#!/bin/bash

CUR_DIR=$(realpath $(dirname $0))
ROOT_DIR=$(realpath $CUR_DIR/../..)
cd $ROOT_DIR

INCSV=${INCSV:='twitter_cont'}
INPUT="hdfs://100.109.192.161:9000/user/plato/data/${INCSV}.csv"
OUTPUT="hdfs://100.109.192.161:9000/user/plato/${INCSV}_fuf"

# program config
NOT_ADD_REVERSED_EDGE=${NOT_ADD_REVERSED_EDGE:=true}  # let plato auto add reversed edge or not
PART_BY_IN=false
ALPHA=-1
OUTER_ITERATION=100
INNER_ITERATION=80

# mpi related
WNUM=4
WCORES=4
ALL_HOSTS="9.67.166.117 100.109.192.161 100.109.188.177 9.66.174.10"

# env for JAVA && HADOOP
export LD_LIBRARY_PATH=${JAVA_HOME}/jre/lib/amd64/server:${LD_LIBRARY_PATH}

# env for hadoop
export CLASSPATH=${HADOOP_HOME}/etc/hadoop:`find ${HADOOP_HOME}/share/hadoop/ | awk '{path=path":"$0}END{print path}'`
export LD_LIBRARY_PATH="${HADOOP_HOME}/lib/native":${LD_LIBRARY_PATH}

run_fuf()
{
    MAIN="$ROOT_DIR/bazel-bin/example/fast_unfolding_simple" # process name

    export MPIRUN_CMD=${MPIRUN_CMD:="$ROOT_DIR/3rd/mpich/bin/mpiexec.hydra"}

    PARAMS+=" --threads ${WCORES}"
    PARAMS+=" --input ${INPUT} --output ${OUTPUT} --is_directed=${NOT_ADD_REVERSED_EDGE}"
    PARAMS+=" --outer_iteration ${OUTER_ITERATION} --inner_iteration ${INNER_ITERATION}"

    chmod 777 ${MAIN}
    ${MPIRUN_CMD} -n ${WNUM} -hosts ${HOSTS} ${MAIN} ${PARAMS}
}

grep_performance()
{
    echo $LOG_FILE
    tail -n 4 $LOG_FILE
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
    LOG_FILE="$ROOT_DIR/scripts/log/${INCSV}.fuf.${HOST_NUM}.${OUTER_ITERATION}.${INNER_ITERATION}.log"
    run_fuf > $LOG_FILE 2>&1
    grep_performance
}

echo "[Performance]:"
run_single 1
run_single 2
run_single 3
run_single 4
