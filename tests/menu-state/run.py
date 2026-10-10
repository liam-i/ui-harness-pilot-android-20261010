from pathlib import Path
import argparse,subprocess,json,hashlib,shutil,tempfile
from datetime import datetime,timezone

p=argparse.ArgumentParser();p.add_argument('--jdk',required=True);p.add_argument('--record',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[2];out=Path(a.record).resolve();out.mkdir(parents=True,exist_ok=False)
sources=[root/'app/src/main/java/io/harness/menu/MenuState.java',Path(__file__).with_name('MenuStateTest.java')]
for source in sources:shutil.copyfile(source,out/source.name)
record={'started_at':datetime.now(timezone.utc).isoformat(),'sources':[{'path':str(s.relative_to(root)),'sha256':hashlib.sha256(s.read_bytes()).hexdigest()} for s in sources],'commands':[]}
with tempfile.TemporaryDirectory(prefix='menu-state-',dir='/private/tmp') as temp:
    for command in [[str(Path(a.jdk)/'bin/javac'),'-d',temp,*map(str,sources)],[str(Path(a.jdk)/'bin/java'),'-cp',temp,'io.harness.menu.MenuStateTest']]:
        r=subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=60)
        record['commands'].append({'args':command,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        print(r.stdout,end='');print(r.stderr,end='')
        if r.returncode:break
record['exit']=r.returncode;record['finished_at']=datetime.now(timezone.utc).isoformat()
(out/'result.json').write_text(json.dumps(record,indent=2)+'\n')
raise SystemExit(r.returncode)
