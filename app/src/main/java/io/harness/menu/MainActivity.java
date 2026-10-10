package io.harness.menu;

import android.app.Activity;
import android.os.Bundle;
import android.widget.FrameLayout;

public final class MainActivity extends Activity {
    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        // Callable native surface for the first real rendering RED; no menu implementation yet.
        setContentView(new FrameLayout(this));
    }
}
