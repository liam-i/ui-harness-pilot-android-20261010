package io.harness.menu;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.Typeface;
import org.json.JSONObject;
import java.io.InputStream;
import java.security.MessageDigest;
import java.util.LinkedHashMap;
import java.util.Map;

/** The approved assets are consumed as bytes, without resource-density inference. */
public final class DesignResources {
    public final JSONObject tokens;
    public final Map<String, String> loaded = new LinkedHashMap<>();
    public final Map<Bitmap, String> bitmaps = new java.util.IdentityHashMap<>();
    private final Context context;
    public DesignResources(Context context) {
        this.context = context;
        try { tokens = new JSONObject(new String(read("tokens.json"), java.nio.charset.StandardCharsets.UTF_8)); }
        catch (Exception e) { throw new IllegalStateException("Approved tokens unavailable", e); }
    }
    public byte[] read(String name) {
        try (InputStream stream = context.getAssets().open("ui/" + name)) {
            byte[] bytes = stream.readAllBytes();
            StringBuilder digest = new StringBuilder();
            for (byte b : MessageDigest.getInstance("SHA-256").digest(bytes)) digest.append(String.format("%02x", b & 255));
            loaded.put(name, digest.toString());
            return bytes;
        } catch (Exception e) { throw new IllegalStateException("Approved asset unavailable: " + name, e); }
    }
    public Bitmap bitmap(String name) {
        byte[] bytes = read(name);
        BitmapFactory.Options options = new BitmapFactory.Options(); options.inScaled = false;
        Bitmap bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.length, options);
        if (bitmap == null) throw new IllegalStateException("Invalid approved bitmap: " + name);
        bitmaps.put(bitmap, name);
        return bitmap;
    }
    public int color(String key) { return Color.parseColor(tokens.optJSONObject("colors").optString(key)); }
    public float size(String role) { return (float) tokens.optJSONObject("font").optJSONObject(role).optDouble("sp"); }
    public int weight(String role) { return tokens.optJSONObject("font").optJSONObject(role).optInt("weight"); }
    public float dimension(String key) { return (float) tokens.optJSONObject("layout").optDouble(key); }
    public Typeface typeface(String role) {
        int weight = weight(role);
        if (android.os.Build.VERSION.SDK_INT >= 28) return Typeface.create(Typeface.create("sans-serif", Typeface.NORMAL), weight, false);
        return Typeface.create(weight == 500 ? "sans-serif-medium" : "sans-serif", weight == 700 ? Typeface.BOLD : Typeface.NORMAL);
    }
}
