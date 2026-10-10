package com.example.fixtures;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.Test;

/**
 * Deterministic flaky tests for rerunFailingTestsCount. Attempts are counted in files under target/,
 * so the counts survive whether Surefire reruns a test in the same JVM or a new one.
 */
public class FlakyTest {

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
    public void passes() {
        assertTrue(true);
    }

    @Test
    public void failsOnceThenPasses() {
        assertTrue("the first attempt fails", attempt("fails-once") > 1);
    }

    @Test
    public void errorsOnceThenPasses() {
        if (attempt("errors-once") == 1) {
            throw new IllegalStateException("the first attempt throws");
        }
    }

    @Test
    public void alwaysFails() {
        assertEquals("fails on every attempt", "expected", "actual");
    }

    @Test
    public void alwaysErrors() {
        throw new IllegalStateException("throws on every attempt");
    }
}
