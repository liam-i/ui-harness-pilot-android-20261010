package io.harness.menu;

public final class MenuStateTest {
    static int count;
    static void check(boolean ok, String message) {
        if (!ok) throw new AssertionError(message);
    }
    static void test(String name, Runnable body) {
        body.run(); count++; System.out.println("PASS " + name);
    }
    public static void main(String[] args) {
        test("cold process starts with 128 and disabled Continue", () -> {
            MenuState s = new MenuState();
            check(s.best() == 128, "cold start best must be 128; got " + s.best());
            check(s.sessionId().isEmpty(), "cold process must not invent session");
            check(s.screen().equals("menu/default"), "cold start must show default menu");
            s.continueGame();
            check(s.sessionId().isEmpty() && s.screen().equals("menu/default"), "disabled Continue must not transition");
        });
        test("New replaces sessions and Continue preserves identity", () -> {
            MenuState s = new MenuState();
            s.newGame();
            check(!s.sessionId().isEmpty(), "New must create a real session identity");
            String first = s.sessionId();
            check(s.screen().equals("session/active") && s.best() == 128, "New must open session without resetting score");
            s.menu(); check(s.screen().equals("menu/resumable"), "Menu must enable continuation");
            s.continueGame(); check(s.sessionId().equals(first) && s.screen().equals("session/active"), "Continue must resume the same session");
            s.menu(); s.newGame(); check(!s.sessionId().equals(first), "New must replace existing session");
        });
        System.out.println("TOTAL " + count);
    }
}
