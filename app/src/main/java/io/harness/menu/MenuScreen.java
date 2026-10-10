package io.harness.menu;

import android.content.Context;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.view.accessibility.AccessibilityNodeInfo;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.TextView;
import android.util.TypedValue;

/** Native controls placed in the approved responsive composition. */
public final class MenuScreen extends FrameLayout {
    public final MenuState state;
    public final DesignResources design;
    public int insetLeft, insetTop, insetRight, insetBottom;
    private final float density, scale;
    private boolean compact;
    private float width, height, left, top, bottom, contentWidth;

    public MenuScreen(Context context, MenuState state) {
        super(context); this.state = state; design = new DesignResources(context);
        density = getResources().getDisplayMetrics().density;
        scale = getResources().getConfiguration().fontScale;
        setTag("root"); setBackgroundColor(design.color("cream"));
        setClipChildren(false);
    }
    public void insets(int l, int t, int r, int b) {
        if (l == insetLeft && t == insetTop && r == insetRight && b == insetBottom) return;
        insetLeft=l; insetTop=t; insetRight=r; insetBottom=b; render();
    }
    @Override protected void onSizeChanged(int w, int h, int oldw, int oldh) { super.onSizeChanged(w,h,oldw,oldh); render(); }
    private int px(float dp) { return Math.round(dp * density); }
    private boolean large() { return scale > 1.15f; }
    private float fontScale() { return large() ? 1.3f : 1f; }
    private GradientDrawable shape(String color, float radius, boolean stroke) {
        GradientDrawable d = new GradientDrawable(); d.setColor(design.color(color)); d.setCornerRadius(px(radius));
        if (stroke) d.setStroke(px(1), design.color("border")); return d;
    }
    private void place(FrameLayout parent, View v, String name, float x, float y, float w, float h) {
        v.setTag(name);
        FrameLayout.LayoutParams p = new FrameLayout.LayoutParams(px(x+w)-px(x), px(y+h)-px(y));
        p.leftMargin=px(x); p.topMargin=px(y); parent.addView(v,p);
    }
    private FrameLayout panel(FrameLayout parent, String name, float x,float y,float w,float h,String color,float radius,boolean stroke) {
        FrameLayout v=new FrameLayout(getContext()); v.setBackground(shape(color,radius,stroke));
        place(parent,v,name,x,y,w,h); return v;
    }
    // Position the actual TextView's baseline, not a simulated text rectangle.
    private TextView text(FrameLayout parent, String name, String copy, String role, String color,
                          float x, float baseline, float w, boolean center, float lineHeight) {
        TextView v = new TextView(getContext()); v.setText(copy); v.setIncludeFontPadding(false);
        v.setPadding(0,0,0,0); v.setLetterSpacing(0); v.setTypeface(design.typeface(role));
        v.setTextSize(TypedValue.COMPLEX_UNIT_PX, design.size(role) * fontScale() * density);
        v.setTextColor(design.color(color)); v.setGravity(center ? Gravity.CENTER_HORIZONTAL : Gravity.LEFT);
        v.setBreakStrategy(android.text.Layout.BREAK_STRATEGY_SIMPLE); v.setHyphenationFrequency(0);
        if (lineHeight > 0) v.setLineSpacing(px(lineHeight) - v.getPaint().getFontMetricsInt(null),1);
        v.measure(MeasureSpec.makeMeasureSpec(px(w),MeasureSpec.EXACTLY),MeasureSpec.makeMeasureSpec(0,MeasureSpec.UNSPECIFIED));
        float y=baseline-v.getBaseline()/density;
        place(parent,v,name,x,y,w,v.getMeasuredHeight()/density); return v;
    }
    private Control control(FrameLayout parent, String name, String copy, float x,float y,float w,float h,
                            String color,boolean border,Runnable action) {
        Control c=new Control(getContext(),copy); c.setBackground(shape(color,design.dimension("button_radius_dp"),border));
        c.setOnClickListener(v->{action.run();render();}); place(parent,c,name,x,y,w,h); return c;
    }
    private void buttonText(Control c,String name,String copy,float w,float baseline) {
        TextView v=text(c,name,copy,"button","ink",0,baseline,w,true,0);
        v.setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO);
    }
    private void icon(FrameLayout parent,String name,String asset,float x,float y,float alpha) {
        ImageView v=new ImageView(getContext()); v.setImageBitmap(design.bitmap(asset));
        v.setScaleType(ImageView.ScaleType.FIT_XY); v.setAlpha(alpha);
        v.setContentDescription(null); v.setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO);
        place(parent,v,name,x,y,24,24);
    }
    public void render() {
        if (getWidth()==0 || getHeight()==0) return;
        removeAllViews(); width=getWidth()/density; height=getHeight()/density;
        contentWidth=Math.min(design.dimension("max_content_width_dp"),width-(insetLeft+insetRight)/density-48);
        left=insetLeft/density+(width-(insetLeft+insetRight)/density-contentWidth)/2;
        top=insetTop/density+design.dimension("content_vertical_padding_dp");
        bottom=height-insetBottom/density-design.dimension("content_vertical_padding_dp");
        compact=large() && width<=360.5f;
        FrameLayout content=new FrameLayout(getContext()); place(this,content,"content",0,0,width,height);
        if (state.screen().equals("session/active")) session(content); else menu(content);
        if(state.modal()) { content.setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS); modal(); }
    }
    private void menu(FrameLayout content) {
        float header=large()?152:120, footer=large()?29:22;
        float mainHeight=compact?290:large()?310:300;
        float mainY=compact?top+header+12:top+header+(bottom-top-header-mainHeight-footer)/2;
        text(content,"eyebrow","A LITTLE EVERY DAY","label","secondary_text",left,top+(large()?15:12),contentWidth,true,0);
        text(content,"title","2048","title","ink",left,top+(large()?100:78),contentWidth,true,0);
        text(content,"tagline","Make room for your next move.","body","secondary_text",left,top+(large()?145:114),contentWidth,true,0);
        float scoreH=large()?102:92;
        FrameLayout card=panel(content,"score-card",left,mainY,contentWidth,scoreH,"paper",20,true);
        text(card,"score-caption","YOUR BEST","label","secondary_text",0,large()?27:24,contentWidth,true,0);
        text(card,"best",String.valueOf(state.best()),"score","ink",0,large()?79:64,contentWidth,true,0);
        float continueY=mainY+scoreH+(compact?12:24), gap=compact?8:12;
        boolean enabled=!state.sessionId().isEmpty();
        Control resume=control(content,"continue","Continue",left,continueY,contentWidth,56,"panel",enabled,state::continueGame);
        resume.setEnabled(enabled);
        float textX=large()?93:103.5f, textW=large()?102:81;
        TextView resumeText=text(resume,"continue-label","Continue","button","ink",textX,large()?36:34,textW,false,0);
        resumeText.setAlpha(enabled?1:.38f); resumeText.setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO);
        icon(resume,"arrow","asset-arrow.png",large()?196:185.5f,16,enabled?1:.38f);
        Control next=control(content,"new-game","New game",left,continueY+56+gap,contentWidth,56,"accent",false,state::newGame);
        buttonText(next,"new-label","New game",contentWidth,large()?36:34);
        Control reset=control(content,"reset-best","Reset best score",left,continueY+112+2*gap,contentWidth,48,"cream",false,state::askReset);
        icon(reset,"reset-icon","asset-reset.png",large()?51:71.5f,12,1);
        TextView label=text(reset,"reset-label","Reset best score","button","ink",large()?83:103.5f,large()?32:30,contentWidth-(large()?83:103.5f),false,0);
        label.setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO);
        float footerY=compact?mainY+mainHeight+12:bottom-footer;
        text(content,"footer","Small moves. Fresh possibilities.","body","secondary_text",left,footerY+(large()?22:16),contentWidth,true,0);
    }
    private void session(FrameLayout content) {
        float header=large()?(compact?213:217):170;
        text(content,"session-title","Let's\nbegin.","title","ink",left,top+(large()?72:55),contentWidth,false,large()?87:67);
        text(content,"session-copy","Session started.","body","secondary_text",left,top+(large()?(compact?205:209):163),contentWidth,false,0);
        float menuY=bottom-56;
        float boardY=compact?top+header+8:top+header+(menuY-top-header-264)/2;
        if(compact)menuY=boardY+264+8;
        FrameLayout board=panel(content,"board",(width-264)/2,boardY,264,264,"border",20,false);
        for(int i=0;i<4;i++) {
            FrameLayout tile=panel(board,"tile-"+i,12+(i%2)*126,12+(i/2)*126,114,114,i<2?"paper":"panel",12,false);
            if(i<2)text(tile,"tile-value-"+i,"2","tile","ink",0,large()?74.5f:70.5f,114,true,0);
        }
        Control back=control(content,"menu-back","Menu",left,menuY,contentWidth,56,"accent",false,state::menu);
        buttonText(back,"menu-label","Menu",contentWidth,large()?36:34);
    }
    private void modal() {
        FrameLayout overlay=new FrameLayout(getContext()); overlay.setBackgroundColor(0x66423B2E); overlay.setClickable(true);
        place(this,overlay,"modal-overlay",0,0,width,height);
        float h=large()?258:203, y=(insetTop/density+height-insetBottom/density-h)/2;
        FrameLayout dialog=panel(overlay,"dialog",left,y,312,h,"paper",28,false);
        dialog.setClickable(true); dialog.setAccessibilityPaneTitle("A fresh start?");
        text(dialog,"dialog-title","A fresh start?","dialog_title","ink",24,large()?56:48,264,false,0);
        String body=large()?"Your best score will return to\nzero. Your current session\nstays here.":"Your best score will return to zero.\nYour current session stays here.";
        text(dialog,"dialog-copy",body,"body","secondary_text",24,large()?100:84,264,false,large()?31:24);
        float buttonY=h-24-56;
        Control cancel=control(dialog,"cancel","Cancel",24,buttonY,127,56,"panel",true,state::cancelReset);
        buttonText(cancel,"cancel-label","Cancel",127,large()?36:34);
        Control confirm=control(dialog,"confirm-reset","Reset",163,buttonY,125,56,"accent",false,state::confirmReset);
        buttonText(confirm,"confirm-label","Reset",125,large()?36:34);
    }
    private static final class Control extends FrameLayout {
        private final String label;
        Control(Context context,String label) {
            super(context); this.label=label; setFocusable(true); setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_YES);
            setDescendantFocusability(FOCUS_BLOCK_DESCENDANTS);
        }
        @Override public CharSequence getAccessibilityClassName(){return "android.widget.Button";}
        @Override public void onInitializeAccessibilityNodeInfo(AccessibilityNodeInfo info) {
            super.onInitializeAccessibilityNodeInfo(info); info.setText(label); info.setClassName(getAccessibilityClassName());
        }
    }
}
