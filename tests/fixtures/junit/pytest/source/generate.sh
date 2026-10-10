#!/bin/sh
# Generate the pytest JUnit XML fixtures. Runs inside a python:*-slim container; see ../README.md
# for the exact docker command. Usage: generate.sh current|legacy
set -eu
mode="${1:?usage: generate.sh current|legacy}"
out=/work/out

# Work in a writable copy at a neutral path, so tracebacks show /work/sample/...
cp -R /work/source /work/sample
cd /work/sample
python -m venv /work/venv
. /work/venv/bin/activate
pip_install() { pip install --quiet --disable-pip-version-check --no-cache-dir "$@"; }

# Run pytest and accept only the expected exit codes (1: some tests failed; 2: collection error).
run() {
    expected="$1"
    shift
    status=0
    python -m pytest "$@" || status=$?
    case " $expected " in
        *" $status "*) ;;
        *) echo "pytest exited with $status; expected one of: $expected" >&2; exit 1 ;;
    esac
}

if [ "$mode" = legacy ]; then
    pip_install pytest==7.4.4
    python -VV
    pip freeze
    run 1 -o junit_family=xunit2 -o junit_logging=all --junitxml="$out/xunit2-outcomes-pytest7.4.4.xml" tests
    exit 0
fi

pip_install pytest==9.1.1 pytest-repeat==0.9.4 pytest-xdist==3.8.0 pytest-rerunfailures==16.7
python -VV
pip freeze
run 1 -o junit_family=xunit1 -o junit_logging=all --junitxml="$out/xunit1-outcomes.xml" tests
run 1 -o junit_family=xunit2 -o junit_logging=all --junitxml="$out/xunit2-outcomes.xml" tests
run 1 -n 2 --junitxml="$out/xunit2-xdist.xml" tests
run 0 --count 3 --junitxml="$out/xunit2-repeat.xml" repeat
run 2 --junitxml="$out/xunit2-collection-error.xml" broken
run 1 --reruns 2 --junitxml="$out/xunit2-rerunfailures-16.7.xml" reruns

pip_install pytest-rerunfailures==16.6
pip freeze | grep -i rerunfailures
run 1 --reruns 2 --junitxml="$out/xunit2-rerunfailures-16.6.xml" reruns
