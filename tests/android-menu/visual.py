"""Reference SVG shapes/baselines versus actual native view geometry and screenshot pixels."""
from pathlib import Path
import json,math,re,struct,zlib
import xml.etree.ElementTree as ET

ROLES={'eyebrow':'label','title':'title','tagline':'body','score-caption':'label','best':'score',
       'continue-label':'button','new-label':'button','reset-label':'button','footer':'body',
       'session-title':'title','session-copy':'body','menu-label':'button','tile-value-0':'tile','tile-value-1':'tile',
       'dialog-title':'dialog_title','dialog-copy':'body','cancel-label':'button','confirm-label':'button'}
SIZES={'label':12,'title':64,'body':16,'score':36,'button':18,'tile':40,'dialog_title':26}
WEIGHTS={'label':500,'title':700,'body':400,'score':500,'button':500,'tile':500,'dialog_title':700}
SECONDARY={'eyebrow','tagline','score-caption','footer','session-copy','dialog-copy'}

def png(data):
    pos=8;compressed=bytearray();header=None
    while pos<len(data):
        size=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];chunk=data[pos+8:pos+8+size]
        if kind==b'IHDR':header=struct.unpack('>IIBBBBB',chunk)
        if kind==b'IDAT':compressed.extend(chunk)
        pos+=size+12
    w,h,depth,kind,compression,filter_,interlace=header
    assert depth==8 and kind in [2,6] and (compression,filter_,interlace)==(0,0,0)
    ch=3 if kind==2 else 4;stride=w*ch;raw=zlib.decompress(compressed);last=bytearray(stride);rows=[]
    for y in range(h):
        off=y*(stride+1);mode=raw[off];row=bytearray(raw[off+1:off+1+stride])
        if mode:
            for i in range(stride):
                a=row[i-ch] if i>=ch else 0;b=last[i];c=last[i-ch] if i>=ch else 0
                if mode==1:v=a
                elif mode==2:v=b
                elif mode==3:v=(a+b)//2
                elif mode==4:
                    p=a+b-c;pa,pb,pc=abs(p-a),abs(p-b),abs(p-c);v=a if pa<=pb and pa<=pc else b if pb<=pc else c
                else:raise ValueError('PNG filter')
                row[i]=(row[i]+v)&255
        rows.append(row);last=row
    return w,h,lambda x,y:tuple(rows[y][x*ch:x*ch+3])

def validate_visual(s,o,data,geometry_only=False):
    d=o['density'];w,h=o['width']/d,o['height']/d;insets=[v/d for v in o['insets']]
    large=o['fontScale']>1.15;compact=large and s.device['key']=='small'
    family='session-active' if o['state']['screen']=='session/active' else 'dialog-reset-empty' if o['state']['modal'] else 'menu-default'
    basename=s.device['key']+('-f130-' if large else '-f100-')+family
    package=s.project/'design-inputs/packages/UI-FIGMA-ANDROID-MENU/U001'
    tree=ET.parse(package/'references'/(basename+'.svg'))
    rectangles=[e.attrib for e in tree.iter() if e.tag.endswith('rect') and e.get('fill') not in [None,'white']]
    refw=float(rectangles[0]['width']);refh=float(rectangles[0]['height'])
    dx=(w-refw)/2;dy_top=insets[1]-24;dy_bottom=h-refh-(insets[3]-32);dy_mid=(dy_top+dy_bottom)/2
    # The reference coordinates are actual exported rectangles, including stroke center insets.
    product=[r for r in rectangles if r.get('rx') and float(r['height'])>10]
    def rect(r,anchor):
        border=float(r.get('rx','0')) in [19.5,15.5]
        half=.5 if border else 0
        x=float(r.get('x',0))-half+dx;y=float(r.get('y',0))-half+anchor
        return [x,y,x+float(r['width'])+2*half,y+float(r['height'])+2*half]
    shapes={};colors={};baselines={};radii={}
    def radius(r):return float(r['rx'])+(.5 if float(r['rx']) in [19.5,15.5] else 0)
    if family=='session-active':
        for name,r in zip(['board','tile-0','tile-1','tile-2','tile-3','menu-back'],product):
            anchor=dy_top if compact else dy_bottom if name=='menu-back' else dy_mid
            shapes[name]=rect(r,anchor);colors[name]=r['fill'];radii[name]=radius(r)
        baselines={'session-title':[108,195] if large else [91,158],
                   'session-copy':[241 if compact else 245] if large else [199]}
        for name in baselines:baselines[name]=[x+dy_top for x in baselines[name]]
        for i in [0,1]:baselines['tile-value-'+str(i)]=[shapes['tile-'+str(i)][1]+(74.5 if large else 70.5)]
        baselines['menu-label']=[shapes['menu-back'][1]+(36 if large else 34)]
    else:
        for name,r in zip(['score-card','continue','new-game'],product[:3]):
            shapes[name]=rect(r,dy_top if compact else dy_mid);colors[name]=r['fill'];radii[name]=radius(r)
        # The reset hit area is the final 48 dp of the actual exported action clip.
        clips=[e for e in tree.iter() if e.tag.endswith('clipPath')]
        action=[r.attrib for c in clips for r in c if r.tag.endswith('rect') and float(r.get('height',0)) in [176,184]][-1]
        xy=list(map(float,re.findall(r'[-0-9.]+',action['transform'])));reset_y=xy[1]+float(action['height'])-48+(dy_top if compact else dy_mid)
        shapes['reset-best']=[xy[0]+dx,reset_y,xy[0]+dx+312,reset_y+48];colors['reset-best']='#FAF7EF'
        base=shapes['score-card'][1];continue_y=shapes['continue'][1]
        for name,y in [('eyebrow',51 if large else 48),('title',136 if large else 114),('tagline',181 if large else 150)]:baselines[name]=[y+dy_top]
        baselines.update({'score-caption':[base+(27 if large else 24)],'best':[base+(79 if large else 64)],
                          'continue-label':[continue_y+(36 if large else 34)],'new-label':[shapes['new-game'][1]+(36 if large else 34)],
                          'reset-label':[reset_y+(32 if large else 30)]})
        baselines['footer']=[524+dy_top if compact else refh-(51 if large else 50)+dy_bottom]
        for name,x,y in [('arrow',196 if large else 185.5,continue_y+16),('reset-icon',51 if large else 71.5,reset_y+12)]:
            x+=shapes['continue'][0];shapes[name]=[x,y,x+24,y+24]
        if family=='dialog-reset-empty':
            for name,r in zip(['dialog','cancel','confirm-reset'],product[3:]):shapes[name]=rect(r,dy_mid);colors[name]=r['fill'];radii[name]=radius(r)
            dialog_y=shapes['dialog'][1]
            baselines.update({'dialog-title':[dialog_y+(56 if large else 48)],
                              'dialog-copy':[dialog_y+x for x in ([100,131,162] if large else [84,108])],
                              'cancel-label':[shapes['cancel'][1]+(36 if large else 34)],
                              'confirm-label':[shapes['confirm-reset'][1]+(36 if large else 34)]})
    metrics={'reference':basename,'reference_frame':[refw,refh],'actual_insets':insets,'shape_deltas_px':{},'baseline_deltas_dp':{}}
    # Collect every geometry difference so a failed assertion retains concrete actual/reference values.
    failures=[]
    for name,expected in shapes.items():
        n=s.node(o,name);deltas=[actual-exp*d for actual,exp in zip(n['bounds'],expected)]
        metrics['shape_deltas_px'][name]=deltas
        if max(map(abs,deltas))>1.01:failures.append(('shape',name,deltas))
        if name in colors and n.get('fill')!='#FF'+colors[name][1:]:failures.append(('fill',name,n.get('fill'),colors[name]))
        if name in radii and abs(n.get('radius',-1)-radii[name]*d)>1.01:failures.append(('radius',name,n.get('radius'),radii[name]*d))
    controls=['cancel','confirm-reset'] if o['state']['modal'] else ['menu-back'] if family=='session-active' else ['continue','new-game','reset-best']
    for i,name in enumerate(controls):
        b=s.node(o,name)['bounds'];x,y,r,bottom=[v/d for v in b]
        if min(r-x,bottom-y)<48-.01:failures.append(('minimum touch',name,b))
        if x<insets[0] or y<insets[1] or r>w-insets[2] or bottom>h-insets[3]:failures.append(('safe area',name,b))
        for other in controls[i+1:]:
            c=s.node(o,other)['bounds'];overlap=min(min(b[2],c[2])-max(b[0],c[0]),min(b[3],c[3])-max(b[1],c[1]))
            if overlap>0:failures.append(('overlap',name,other))
    if not geometry_only:
        if family!='session-active':
            for name in ['continue-label','arrow']:
                actual=s.node(o,name)['alpha'];target=1 if o['state']['session'] else .38
                if abs(actual-target)>.001:failures.append(('Continue alpha',name,actual,target))
        for name,role in ROLES.items():
            matches=[n for n in o['nodes'] if n['name']==name]
            if not matches:continue
            n=matches[0];t=n['text'];target=SIZES[role]*(1.3 if large else 1)*d
            if abs(t['size']-target)>.02:failures.append(('font size',name,t['size'],target))
            if t['weight']!=WEIGHTS[role]:failures.append(('font weight',name,t['weight'],WEIGHTS[role]))
            if t['letterSpacing']!=0:failures.append(('letter spacing',name,t['letterSpacing']))
            color='#FF6B6254' if name in SECONDARY else '#FF423B2E'
            if t['color']!=color:failures.append(('text color',name,t['color'],color))
            targets=baselines[name];actual=[l['baseline']/d for l in t['lines']]
            if len(actual)!=len(targets):failures.append(('text wrapping',name,actual,targets))
            else:
                deltas=[a-b for a,b in zip(actual,targets)];metrics['baseline_deltas_dp'][name]=deltas
                if max(map(abs,deltas))>2:failures.append(('baseline',name,deltas))
            for line in t['lines']:
                b=n['bounds'];visible=n['visibleBounds']
                if line['ellipsis'] or line['width']>b[2]-b[0]+1:failures.append(('text width/ellipsis',name,line,b))
                if line['baseline']+line['ascent']<visible[1]-1 or line['baseline']+line['descent']>visible[3]+1:failures.append(('text clipping',name,line,visible))
        if family=='session-active':s.session_assert(o)
        else:s.menu_assert(o)
        if o['state']['modal']:
            expected="Your best score will return to\nzero. Your current session\nstays here." if large else "Your best score will return to zero.\nYour current session stays here."
            for name,copy in [('dialog-title','A fresh start?'),('dialog-copy',expected),('cancel-label','Cancel'),('confirm-label','Reset')]:s.check('modal exact copy '+name,s.node(o,name)['text']['copy'],copy)
        pw,ph,pixel=png(data);s.check('actual screencap size',[pw,ph],[o['width'],o['height']])
        for name,color in colors.items():
            if o['state']['modal'] and name not in ['dialog','cancel','confirm-reset']:continue
            b=s.node(o,name)['bounds'];x=round((b[0]+b[2])/2);y=round(b[1]+6*d)
            expected=tuple(int(color[i:i+2],16) for i in [1,3,5]);actual=pixel(x,y)
            if actual!=expected:failures.append(('actual pixel fill',name,actual,expected,x,y))
        actual=pixel(round(4*d),round((insets[1]+12)*d));expected=(176,172,162) if o['state']['modal'] else (250,247,239)
        if any(abs(a-b)>1 for a,b in zip(actual,expected)):failures.append(('backdrop actual pixel',actual,expected))
    metrics['failures']=failures
    path=s.out/f'visual-{s.current}-{s.seq:04}.json';path.write_text(json.dumps(metrics,indent=2)+'\n')
    s.check('original visual tolerances '+basename,failures,[])
