package com.example.fixtures;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

/**
 * Deterministic flaky tests for rerunFailingTestsCount. Attempts are counted in files under target/,
 * so the counts survive whether Surefire reruns a test in the same JVM or a new one.
 */
class FlakyTest {

    private static int attempt(String name) {
        try {
            Path file = Path.of("target", "attempts", name);
            Files.createDirectories(file.getParent());
            int count = Files.exists(file) ? Integer.parseInt(Files.readString(file).trim()) + 1 : 1;
            Files.writeString(file, Integer.toString(count));
            return count;
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    @Test
    void passes() {
        assertTrue(true);
    }

    @Test
    void failsOnceThenPasses() {
        assertTrue(attempt("fails-once") > 1, "the first attempt fails");
    }

    @Test
    void errorsOnceThenPasses() {
        if (attempt("errors-once") == 1) {
            throw new IllegalStateException("the first attempt throws");
        }
    }

    @Test
    void alwaysFails() {
        assertEquals("expected", "actual", "fails on every attempt");
    }

    @Test
    void alwaysErrors() {
        throw new IllegalStateException("throws on every attempt");
    }
}
