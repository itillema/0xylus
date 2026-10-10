#!/bin/sh
# Generate the Maven Surefire JUnit XML fixtures. Runs inside a maven:*-eclipse-temurin-21 container;
# see ../README.md for the exact docker command.
set -eu
out=/work/out

# Work in a writable copy at a neutral path, so stack traces show /work/sample/...
cp -R /work/source /work/sample
mvn -v
java -version

# build <project> <surefire version> <junit version, or "-" for the pom's> <output directory>
build() {
    project="$1"
    surefire="$2"
    junit="$3"
    dest="$out/$4"
    cd "/work/sample/$project"
    rm -rf target
    set -- -B -ntp -Dsurefire.version="$surefire" -Dsurefire.rerunFailingTestsCount=2 \
        -Dmaven.test.failure.ignore=true
    if [ "$junit" != "-" ]; then
        set -- "$@" -Djunit.version="$junit"
    fi
    mvn "$@" test
    mkdir -p "$dest"
    cp target/surefire-reports/TEST-*.xml "$dest/"
}

build junit5 3.6.0 6.1.3 surefire-3.6.0/junit6
build junit4 3.6.0 - surefire-3.6.0/junit4
build junit5 3.5.4 5.14.4 surefire-3.5.4/junit5
build junit4 3.5.4 - surefire-3.5.4/junit4
