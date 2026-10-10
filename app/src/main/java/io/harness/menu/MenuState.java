package io.harness.menu;

/** Process-lifetime menu data, independent of views and test observation. */
public final class MenuState {
    private int best = 128;
    private final String process = java.util.UUID.randomUUID().toString();
    private long nextSession;
    private String session = "";
    private boolean active;
    private boolean modal;
    public int best() { return best; }
    public String sessionId() { return session; }
    public String screen() {
        if (modal) return session.isEmpty() ? "dialog/reset-empty" : "dialog/reset-resumable";
        if (active) return "session/active";
        if (best == 0) return session.isEmpty() ? "menu/zero-empty" : "menu/zero-resumable";
        return session.isEmpty() ? "menu/default" : "menu/resumable";
    }
    public boolean modal() { return modal; }
    public void newGame() { if (!modal) { session = process + ":" + (++nextSession); active = true; } }
    public void continueGame() { if (!modal && !session.isEmpty()) active = true; }
    public void menu() { if (!modal) active = false; }
    public void askReset() { if (!active) modal = true; }
    public void cancelReset() { modal = false; }
    public void confirmReset() { if (modal) { best = 0; modal = false; } }
    public boolean back() {
        if (modal) { cancelReset(); return true; }
        if (active) { menu(); return true; }
        return false;
    }
}
