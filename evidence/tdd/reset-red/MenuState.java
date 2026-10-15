package io.harness.menu;

/** Process-lifetime menu data, independent of views and test observation. */
public final class MenuState {
    private int best = 128;
    private final String process = java.util.UUID.randomUUID().toString();
    private long nextSession;
    private String session = "";
    private boolean active;
    public int best() { return best; }
    public String sessionId() { return session; }
    public String screen() {
        if (active) return "session/active";
        return session.isEmpty() ? "menu/default" : "menu/resumable";
    }
    public boolean modal() { return false; }
    public void newGame() { session = process + ":" + (++nextSession); active = true; }
    public void continueGame() { if (!session.isEmpty()) active = true; }
    public void menu() { active = false; }
    public void askReset() { }
    public void cancelReset() { }
    public void confirmReset() { }
    public boolean back() { return false; }
}
