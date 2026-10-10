package io.harness.menu;

/** Minimal callable API; behavior is introduced by the recorded TDD cycles. */
public final class MenuState {
    public int best() { return 0; }
    public String sessionId() { return ""; }
    public String screen() { return ""; }
    public boolean modal() { return false; }
    public void newGame() { }
    public void continueGame() { }
    public void menu() { }
    public void askReset() { }
    public void cancelReset() { }
    public void confirmReset() { }
    public boolean back() { return false; }
}
