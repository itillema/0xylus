package com.example.fixtures;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.junit.Ignore;
import org.junit.Test;

/** Every outcome Surefire reports for JUnit 4, so the fixtures show how each is written. */
public class OutcomesTest {

    @Test
    public void passes() {
        assertTrue(true);
    }

    @Test
    public void failsWithAssertion() {
        assertEquals("arithmetic is broken", 3, 1 + 1);
    }

    @Test
    public void throwsUnexpectedError() {
        throw new IllegalStateException("unexpected state: 42");
    }

    @Test
    @Ignore("not supported on this platform")
    public void ignored() {
    }

    @Test
    public void writesOutput() {
        System.out.println("line written to stdout");
        System.err.println("line written to stderr");
    }

    @Test
    public void failsWithHostileMessage() {
        throw new AssertionError("<b>bold</b> | @here `code` %0A \u202edesrever");
    }
}
