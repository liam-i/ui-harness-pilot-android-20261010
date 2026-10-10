package io.harness.menu;

import android.app.Activity;
import android.graphics.Rect;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.GradientDrawable;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.ImageView;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;

/** Debug-only readout of real layout/draw state; no commands, expected values or PASS. */
public final class RuntimeObservation {
    private static final String PROCESS = java.util.UUID.randomUUID().toString();
    private long frame;
    private final Activity activity;
    private final MenuScreen root;
    private RuntimeObservation(Activity activity, MenuScreen root) { this.activity=activity; this.root=root; }
    public static void attach(Activity activity, MenuScreen root) {
        RuntimeObservation observer=new RuntimeObservation(activity,root);
        root.getViewTreeObserver().addOnDrawListener(() -> { observer.frame++; root.post(observer::capture); });
        root.post(new Runnable() {
            @Override public void run() {
                if(activity.isDestroyed())return;
                if(root.hasWindowFocus())root.invalidate();
                root.postDelayed(this,500);
            }
        });
    }
    private void capture() {
        if(root.getWidth()==0 || !root.hasWindowFocus())return;
        try {
            JSONObject o=new JSONObject(); o.put("package",activity.getPackageName());
            o.put("pid",android.os.Process.myPid()); o.put("process",PROCESS);
            o.put("capturedAt",System.currentTimeMillis()); o.put("frame",frame);
            o.put("density",root.getResources().getDisplayMetrics().density);
            o.put("fontScale",root.getResources().getConfiguration().fontScale);
            o.put("orientation",root.getResources().getConfiguration().orientation);
            o.put("width",root.getWidth());o.put("height",root.getHeight());
            o.put("insets",new JSONArray(new int[]{root.insetLeft,root.insetTop,root.insetRight,root.insetBottom}));
            JSONObject state=new JSONObject(); state.put("screen",root.state.screen()); state.put("best",root.state.best());
            state.put("session",root.state.sessionId()); state.put("modal",root.state.modal());o.put("state",state);
            o.put("loaded",new JSONObject(root.design.loaded));o.put("tokens",root.design.tokens);
            JSONArray nodes=new JSONArray();walk(root,nodes);o.put("nodes",nodes);
            File temporary=new File(activity.getFilesDir(),"observation.tmp");
            Files.write(temporary.toPath(),o.toString().getBytes(StandardCharsets.UTF_8));
            if(!temporary.renameTo(new File(activity.getFilesDir(),"observation.json")))throw new java.io.IOException("Atomic observation rename failed");
        } catch(Exception e) { android.util.Log.e("MenuObservation","Observation failed",e); }
    }
    private void walk(View v,JSONArray nodes) throws Exception {
        JSONObject n=new JSONObject();n.put("name",String.valueOf(v.getTag()));n.put("class",v.getClass().getName());
        int[] location=new int[2];v.getLocationOnScreen(location);
        n.put("bounds",new JSONArray(new int[]{location[0],location[1],location[0]+v.getWidth(),location[1]+v.getHeight()}));
        Rect visible=new Rect();n.put("visible",v.getGlobalVisibleRect(visible));
        n.put("visibleBounds",new JSONArray(new int[]{visible.left,visible.top,visible.right,visible.bottom}));
        n.put("enabled",v.isEnabled()); n.put("clickable",v.isClickable());n.put("alpha",v.getAlpha());
        n.put("importantForAccessibility",v.getImportantForAccessibility());n.put("accessibilityClass",v.getAccessibilityClassName());
        n.put("contentDescription",v.getContentDescription()==null?JSONObject.NULL:v.getContentDescription());
        if(v.getBackground() instanceof ColorDrawable)n.put("fill",String.format("#%08X",((ColorDrawable)v.getBackground()).getColor()));
        if(v.getBackground() instanceof GradientDrawable) {
            GradientDrawable d=(GradientDrawable)v.getBackground();
            if(d.getColor()!=null)n.put("fill",String.format("#%08X",d.getColor().getDefaultColor()));
            n.put("radius",d.getCornerRadius());
        }
        if(v instanceof TextView) {
            TextView t=(TextView)v;JSONObject text=new JSONObject();text.put("copy",t.getText());
            text.put("size",t.getTextSize());text.put("weight",t.getTypeface().getWeight());text.put("letterSpacing",t.getLetterSpacing());
            text.put("color",String.format("#%08X",t.getCurrentTextColor()));
            text.put("baseline",location[1]+t.getBaseline());
            JSONArray lines=new JSONArray(); android.text.Layout layout=t.getLayout();
            if(layout!=null)for(int i=0;i<layout.getLineCount();i++) {
                JSONObject line=new JSONObject();line.put("baseline",location[1]+t.getBaseline()+layout.getLineBaseline(i)-layout.getLineBaseline(0));
                line.put("width",layout.getLineWidth(i));line.put("left",location[0]+layout.getLineLeft(i));
                line.put("text",t.getText().subSequence(layout.getLineStart(i),layout.getLineEnd(i)).toString());
                line.put("ellipsis",layout.getEllipsisCount(i));
                line.put("ascent",t.getPaint().ascent());line.put("descent",t.getPaint().descent());lines.put(line);
            }
            text.put("lines",lines);n.put("text",text);
        }
        if(v instanceof ImageView && ((ImageView)v).getDrawable() instanceof BitmapDrawable) {
            android.graphics.Bitmap bitmap=((BitmapDrawable)((ImageView)v).getDrawable()).getBitmap();
            n.put("asset",root.design.bitmaps.get(bitmap));n.put("bitmapWidth",bitmap.getWidth());n.put("bitmapHeight",bitmap.getHeight());
        }
        nodes.put(n);
        if(v instanceof ViewGroup)for(int i=0;i<((ViewGroup)v).getChildCount();i++)walk(((ViewGroup)v).getChildAt(i),nodes);
    }
}
