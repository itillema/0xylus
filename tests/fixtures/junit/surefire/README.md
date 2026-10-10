# Maven Surefire JUnit XML fixtures

This directory holds two kinds of real Surefire output:
- **Generated** (`surefire-3.6.0/` and `surefire-3.5.4/`): produced on 2026-10-10 from the sample projects in
  [`source/`](source/).
- **Wild** (`wild/`): genuine reports that other open source projects committed, copied byte-for-byte with their
  licenses.

Don't edit any of these files by hand.

## Generated reports

| Item | Value |
| --- | --- |
| Generated | 2026-10-10, in Docker, with the container hostname `fixturegen` and the projects copied to `/work/sample` |
| Image | `maven:3.9.16-eclipse-temurin-21@sha256:99e61abcff91a9b1333463bd8451fb18495d6eba9250ac66a338b518f8278320` |
| Tools | Apache Maven 3.9.16; Eclipse Temurin 21.0.12.1; maven-compiler-plugin 3.15.0; maven-resources-plugin 3.4.0 |
| Command | In `/work/sample/<project>`: `mvn -B -ntp -Dsurefire.version=<version> [-Djunit.version=<version>] -Dsurefire.rerunFailingTestsCount=2 -Dmaven.test.failure.ignore=true test` ([`source/generate.sh`](source/generate.sh)) |
| Sample projects | [`source/junit5/`](source/junit5/) and [`source/junit4/`](source/junit4/), written for these fixtures. Their tests fail on purpose; attempt counters in `target/` make the flaky tests deterministic |
| License | Apache-2.0, like this repository |

| Directory | Project | Surefire | Test framework |
| --- | --- | --- | --- |
| `surefire-3.6.0/junit6/` | `source/junit5` | 3.6.0 | JUnit Jupiter 6.1.3 |
| `surefire-3.6.0/junit4/` | `source/junit4` | 3.6.0 | JUnit 4.13.2, through the JUnit Vintage engine that Surefire adds |
| `surefire-3.5.4/junit5/` | `source/junit5` | 3.5.4 | JUnit Jupiter 5.14.4 |
| `surefire-3.5.4/junit4/` | `source/junit4` | 3.5.4 | JUnit 4.13.2, through the `surefire-junit4` provider |

To regenerate, run this from the repository root (POSIX shell syntax), then update the hashes below:

```bash
docker run --rm --hostname fixturegen \
  -v "$PWD/tests/fixtures/junit/surefire/source:/work/source:ro" \
  -v "$PWD/tests/fixtures/junit/surefire:/work/out" \
  maven:3.9.16-eclipse-temurin-21@sha256:99e61abcff91a9b1333463bd8451fb18495d6eba9250ac66a338b518f8278320 \
  sh /work/source/generate.sh
```

| File | SHA-256 |
| --- | --- |
| `surefire-3.6.0/junit6/TEST-com.example.fixtures.FlakyTest.xml` | `0c4db1a745ba417b2e422940d4db57452d33083ea0f255c335f7e611a4313d17` |
| `surefire-3.6.0/junit6/TEST-com.example.fixtures.OutcomesTest.xml` | `01ae4b0e069cd6d8057e1481c33df834830a2b9cf2668f67a1f40fa6543bbd33` |
| `surefire-3.6.0/junit4/TEST-com.example.fixtures.FlakyTest.xml` | `f850a6157c06af01e2c8adafee29ab50985b1b9102b420902bb748de8cd655c4` |
| `surefire-3.6.0/junit4/TEST-com.example.fixtures.OutcomesTest.xml` | `fcfa7fe6a4ca796464842f53516c6e6c3c6cab6f55080fd116cfb5e205b1a033` |
| `surefire-3.6.0/junit4/TEST-com.example.fixtures.ParameterizedValuesTest.xml` | `f584704b7a0757cc081e7b3ccafe2c24fdb52f0624eca060afd37937357ba1fe` |
| `surefire-3.5.4/junit5/TEST-com.example.fixtures.FlakyTest.xml` | `2c00e8d8e770e439a1fa80757ec30a3d2ee9559f6cc5165971be5e1f31f6fc33` |
| `surefire-3.5.4/junit5/TEST-com.example.fixtures.OutcomesTest.xml` | `b6f2487475f25c025d2537b12643a5a52b02c163bb03b12530230a14bd50eb88` |
| `surefire-3.5.4/junit4/TEST-com.example.fixtures.FlakyTest.xml` | `c4d1e6eae5e2ad6696e3e4e10d1bb65680226169f5e53315e69c8904e7317b7d` |
| `surefire-3.5.4/junit4/TEST-com.example.fixtures.OutcomesTest.xml` | `79885f572f7a6aaaab20c2be0763f627f4a5f84546c7497a2a6a67c62a7f51a0` |
| `surefire-3.5.4/junit4/TEST-com.example.fixtures.ParameterizedValuesTest.xml` | `d9745a6e13fe81e383fed1a046356d30afe2611282eed5308c3b89ac7f0a8967` |

## Wild reports

All of these were retrieved on 2026-10-10 through the GitHub contents API (raw blobs), at the commits listed. Their
sizes match the upstream blobs. They are unmodified, so they contain the original authors' usernames and local paths.

| Directory | Source | Commit | License | Produced by |
| --- | --- | --- | --- | --- |
| `wild/camunda/` | [camunda/flaky-test-extractor-maven-plugin](https://github.com/camunda/flaky-test-extractor-maven-plugin), `src/test/resources/surefire-reports/` and `src/test/resources/invalid-xml-examples/` | `dafcc7b8b52c4ecd134a5a95acf1ed7fab37d341` | Apache-2.0 ([text](wild/LICENSES/camunda-flaky-test-extractor-maven-plugin-LICENSE.txt)) | Surefire 3.0.0-M2 to M5 (report version `3.0`; the exact version isn't recorded), JUnit 4, Windows 10, OpenJDK 11.0.2 |
| `wild/junit-plugin-gh-237/` | [jenkinsci/junit-plugin](https://github.com/jenkinsci/junit-plugin), `src/test/resources/hudson/tasks/junit/gh-237/` | `04461ad56caf19b05bc16015f23675883df83d43` | MIT ([text](wild/LICENSES/jenkinsci-junit-plugin-LICENSE.txt)) | Surefire 3.3.1 to 3.5.4 (report version `3.0.2`, no `flakes` attribute), JUnit 4 provider, Linux, Temurin 17.0.11 |

| File | SHA-256 |
| --- | --- |
| `wild/camunda/TEST-com.github.pihme.jenkinstestbed.module1.ErrorTest.xml` | `b10b321c374dde3b200e40c580b07df57bd84074c239fdba323bcc7c9b62403c` |
| `wild/camunda/TEST-com.github.pihme.jenkinstestbed.module1.FailingTest.xml` | `1b7be8c34a8937c780d06154c2d4accb6f2e7961085bcd076c363283373c1d03` |
| `wild/camunda/TEST-com.github.pihme.jenkinstestbed.module1.FlakyErrorTest.xml` | `f0991886ae7a461382694bf6e38f6d3c94b43250e1aa31e24641a05b6e216636` |
| `wild/camunda/TEST-com.github.pihme.jenkinstestbed.module1.FlakyTest.xml` | `7ec3730f6250c51091d931e30b3880ed0c60654713af580d7786125acb88b7e4` |
| `wild/camunda/TEST-com.github.pihme.jenkinstestbed.module1.PassingTest.xml` | `0956185b3a055df9352d3093fec27a5ae36843ea06accfcb96cbee868eb0169b` |
| `wild/camunda/truncated/TEST-io.zeebe.broker.it.clustering.BrokerLeaderChangeTest-it-testrun.xml` | `b5d5e7feb7491244fa09f5e1d3c3fb815b3d641609ec0495ac8c9c117f268231` |
| `wild/junit-plugin-gh-237/TEST-io.olamy.AlwaysFailTest.xml` | `a786df44dac170713d4eb2dd8040890835b29e6d8edc219aa40b83d39673ddf5` |
| `wild/junit-plugin-gh-237/TEST-io.olamy.FlakyTest.xml` | `1223898bfe67743374bc838255a418b886239804014689adbfdaaab8a00f887b` |
| `wild/LICENSES/camunda-flaky-test-extractor-maven-plugin-LICENSE.txt` | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` |
| `wild/LICENSES/jenkinsci-junit-plugin-LICENSE.txt` | `00409d6434e7d83af3f2dc7f9eb2b024e3bcad0aa4aa47ec352c82e34666af85` |

The truncated camunda report is real output that was cut off mid-file, ending in an unclosed CDATA section. It must
be rejected with `MalformedInputError`.

## What the files show

`tests/unit/test_fixture_corpus.py` pins each of these facts.

**Report structure:**
- **Root:** each report is a bare `<testsuite>`, with no `<testsuites>` wrapper. Surefire writes one file per test
  class, and a JUnit Jupiter `@Nested` class appears in its outer class's file with the classname `Outer$Nested`.
- **Order:** entries appear in execution order.

**Retries:**
- **Passing on a rerun:** a test that passes on a rerun keeps its failed attempts as `flakyFailure` or `flakyError`
  children.
- **Never passing:** a test that never passes has a `failure` or `error`, then one `rerunFailure` or `rerunError` per
  rerun.
- **Child content:** each of these children holds a `<stackTrace>`.
- **Element order:** the wild reports write `system-out` and `system-err` before the `rerun*` elements. That's not the
  order Surefire's own XSD declares, so reports must not be validated against it.

**`<testsuite>` totals.** Never trust them. For the same tests, they mean different things in different versions:

| Producer | What `tests` counts | Example |
| --- | --- | --- |
| Surefire 3.6.0 | Unique tests by final result, with a `flakes` attribute | `tests="5"` for five tests |
| Surefire 3.5.4 with JUnit 5 | Fewer than the `<testcase>` elements | `tests="2"` for five tests |
| Surefire 3.5.4 with JUnit 4 | Every run, reruns included | `tests="11"` for five tests |
| The wild reports | Every run, reruns included | `tests="16"` for one test retried 15 times |

**Names:**
- **JUnit Jupiter:** `name` is the method name, never the display name. Parameterized invocations are written as
  `method(Type)[index]`, so the arguments don't appear, and an invocation is identified by its position.
- **JUnit 4:** the Parameterized runner's name pattern applies, for example `rejectsTwo[1: value 2]`.
