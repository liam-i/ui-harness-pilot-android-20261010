package io.harness.menu;

/** Process-lifetime menu data, independent of views and test observation. */
public final class MenuState {
    private int best = 128;
    public int best() { return best; }
    public String sessionId() { return ""; }
    public String screen() { return "menu/default"; }
    public boolean modal() { return false; }
    public void newGame() { }
    public void continueGame() { }
    public void menu() { }
    public void askReset() { }
    public void cancelReset() { }
    public void confirmReset() { }
    public boolean back() { return false; }
}
