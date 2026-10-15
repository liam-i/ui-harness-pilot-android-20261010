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
        for (boolean withSession : new boolean[]{false, true}) {
            test("reset/cancel preserve session; modal blocks background, session=" + withSession, () -> {
                MenuState s = new MenuState();
                if (withSession) { s.newGame(); s.menu(); }
                String original = s.sessionId();
                for (int best : new int[]{128, 0}) {
                    check(s.best() == best, "reset round must begin at expected score");
                    s.askReset();
                    check(s.modal() && s.screen().equals(withSession ? "dialog/reset-resumable" : "dialog/reset-empty"), "ask must present matching modal");
                    s.newGame(); s.continueGame(); s.menu();
                    check(s.modal() && s.sessionId().equals(original), "background operations must not penetrate modal");
                    s.cancelReset();
                    check(!s.modal() && s.best() == best && s.sessionId().equals(original), "Cancel must preserve every value");
                    s.askReset(); s.confirmReset();
                    check(s.best() == 0 && !s.modal() && s.sessionId().equals(original), "Reset must only clear score");
                    check(s.screen().equals(withSession ? "menu/zero-resumable" : "menu/zero-empty"), "zero menu must preserve session availability");
                }
                if (withSession) { s.continueGame(); check(s.sessionId().equals(original), "zero score must not delete session"); s.menu(); }
                s.newGame(); check(s.best() == 0 && !s.sessionId().equals(original), "New after zero must work without restoring score");
            });
        }
        System.out.println("TOTAL " + count);
    }
}
