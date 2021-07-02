#!/bin/bash

CUR_DIR=$(realpath $(dirname $0))
ROOT_DIR=$(realpath $CUR_DIR/../..)
cd $ROOT_DIR

INCSV=${INCSV:='twitter_cont'}
INPUT="hdfs://100.109.192.161:9000/user/plato/data/${INCSV}.csv"
OUTPUT="hdfs://100.109.192.161:9000/user/plato/${INCSV}"
ITERATIONS=1000
NOT_ADD_REVERSED_EDGE=${NOT_ADD_REVERSED_EDGE:=true}  # let plato auto add reversed edge or not

run_lpa()
{
    MAIN="$ROOT_DIR/bazel-bin/example/lpa" # process name

    WNUM=4
    WCORES=4

    PART_BY_IN=false
    ALPHA=-1

    export MPIRUN_CMD=${MPIRUN_CMD:="$ROOT_DIR/3rd/mpich/bin/mpiexec.hydra"}

    PARAMS+=" --threads ${WCORES}"
    PARAMS+=" --input ${INPUT} --output ${OUTPUT} --is_directed=${NOT_ADD_REVERSED_EDGE}"
    PARAMS+=" --iterations ${ITERATIONS}"

    # env for JAVA && HADOOP
    export LD_LIBRARY_PATH=${JAVA_HOME}/jre/lib/amd64/server:${LD_LIBRARY_PATH}

    # env for hadoop
    export CLASSPATH=${HADOOP_HOME}/etc/hadoop:`find ${HADOOP_HOME}/share/hadoop/ | awk '{path=path":"$0}END{print path}'`
    export LD_LIBRARY_PATH="${HADOOP_HOME}/lib/native":${LD_LIBRARY_PATH}

    chmod 777 ${MAIN}
    ${MPIRUN_CMD} -n ${WNUM} -hosts ${HOSTS} ${MAIN} ${PARAMS}
}

grep_performance()
{
    echo $LOG_FILE
    cat $LOG_FILE | grep "lpa calculation done"
}

echo "[Performance]:"

HOSTS='9.67.166.117'
LOG_FILE="$ROOT_DIR/scripts/log/${INCSV}.1.${ITERATIONS}.log"
run_lpa > $LOG_FILE 2>&1
grep_performance

HOSTS='9.67.166.117,100.109.192.161'
LOG_FILE="$ROOT_DIR/scripts/log/${INCSV}.2.${ITERATIONS}.log"
run_lpa > $LOG_FILE 2>&1
grep_performance

HOSTS='9.67.166.117,100.109.192.161,100.109.188.177'
LOG_FILE="$ROOT_DIR/scripts/log/${INCSV}.3.${ITERATIONS}.log"
run_lpa > $LOG_FILE 2>&1
grep_performance

HOSTS='9.67.166.117,100.109.192.161,100.109.188.177,9.66.174.10'
LOG_FILE="$ROOT_DIR/scripts/log/${INCSV}.4.${ITERATIONS}.log"
run_lpa > $LOG_FILE 2>&1
grep_performance
