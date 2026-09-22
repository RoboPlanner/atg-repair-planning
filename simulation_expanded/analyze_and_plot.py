"""Aggregate all frozen outcomes and render manuscript figures with Python."""
from pathlib import Path
import json,csv,hashlib,subprocess,collections
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

W=Path(__file__).resolve().parent;E=W/'evaluation_frozen_v1';P=W/'planning_frozen_v2';F=W/'figures';F.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
rows=read(E/'summaries.json');check=read(E/'independent_verification.json');planning=read(P/'records.json')
assert len(rows)==240 and check['total']==240 and check['integrity_valid']==240 and check['outcome_agreement']==240
assert all('runtime_error' not in r for r in rows)
tasks=[f'T{i:02d}' for i in range(1,9)]
titles=['Parallel sorting','Shared inspection','Synchronized kitting','Two-stage shared service','Cooperative transfer','Two-leg transfer','Loading and transfer','Transfer and unloading']
zh=['并行分拣','共享检测工位','同步配套','两阶段共享服务','协作搬运','两段协作搬运','装盘后搬运','搬运后卸载']
conditions=['nominal','heavy','low_friction','pose_bias','fast']
labels=['Nominal','Mass ×5','Low friction','Pose bias','Half windows']
methods=['audit_only','field_match_compressed','full'];profiles=['fields_only','wrong_labels','conservative_order','missing_producer']
def csvout(name,data):
 with (F/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
nominal=[];stress=[];pc=[]
for task,title,cn in zip(tasks,titles,zh):
 a=[r for r in rows if r['task']==task and r['condition']=='nominal' and r['mode']=='full'];b=[r for r in rows if r['task']==task and r['condition']=='nominal' and r['mode']=='serial']
 assert len(a)==len(b)==5
 nominal.append({'task':task,'title':title,'title_zh':cn,'nodes':a[0]['nodes'],'B_nodes':a[0]['cooperative_nodes'],'full_success':sum(x['execution_success'] for x in a),'serial_success':sum(x['execution_success'] for x in b),'n_each':5,'full_window_s':a[0]['scheduled_window_s'],'serial_window_s':b[0]['scheduled_window_s'],'window_reduction_percent':100*(1-a[0]['scheduled_window_s']/b[0]['scheduled_window_s']),'full_max_final_error_mm':1000*max(v for x in a for v in x['goal_errors_m'].values())})
 for condition in conditions:
  group=[r for r in rows if r['task']==task and r['condition']==condition and r['mode']=='full'];assert len(group)==5
  stress.append({'task':task,'condition':condition,'success':sum(x['execution_success'] for x in group),'n':5})
for profile in profiles:
 for method in methods:
  group=[r for r in planning if r['profile']==profile and r['method']==method];assert len(group)==8
  pc.append({'profile':profile,'method':method,'accepted':sum(x['accepted'] for x in group),'n':8})
failure_map={'pick_L:lift_height':'Pick check','transfer1:target_position':'Transfer check','place_R:target_position':'Place check','final_position':'Final-state check'}
failed=[r for r in check['records'] if not r['execution_success']]
first=collections.Counter(failure_map[r['physical_failure_reasons'][0]] for r in failed)
failure=[{'first_failed_check':k,'count':first[k]} for k in failure_map.values()]
totals=[{'condition':c,'success':sum(s['success'] for s in stress if s['condition']==c),'n':40} for c in conditions]
summary={'nominal':nominal,'condition_totals':totals,'planning':pc,'first_failure_categories':failure,'records':240,'execution_successes':184,'physical_failures':56,'integrity_valid':check['integrity_valid'],'online_offline_agreement':check['outcome_agreement'],'planning_settings':96,'planned_window_mean_reduction_percent':float(np.mean([n['window_reduction_percent'] for n in nominal])),'limitations':['Eight author-constructed templates; five perturbations are repeats within each template.','Fixed skill windows, not measured hardware speed.','No natural LLM-error claim; same-compression comparator ties on accepted inputs.','Physical stress changes are absent from the discrete audit contract.']}
(W/'aggregate_results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
for name,data in [('figure10_nominal_windows',nominal),('figure10_planning_controls',pc),('figure11_stress_success',stress),('figure11_first_failures',failure),('simulation_condition_totals',totals)]:csvout(name,data)
flat=[]
for r in rows:flat.append({k:v for k,v in r.items() if not isinstance(v,(list,dict))})
csvout('all_240_runs',flat)
font=font_manager.findfont('Times New Roman',fallback_to_default=False)
plt.rcParams.update({'font.family':'Times New Roman','font.size':10,'axes.labelsize':10.5,'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':10,'axes.linewidth':.65,'svg.fonttype':'none','pdf.fonttype':42,'ps.fonttype':42,'savefig.facecolor':'white'})
def tidy(ax):
 ax.spines[['top','right']].set_visible(False);ax.tick_params(length=3,width=.6);ax.set_axisbelow(True);ax.grid(axis='y',color='#e3e6e9',lw=.5)
def export(fig,name):
 for ext in ['svg','pdf','png','tiff']:
  kwargs={'dpi':600} if ext in ['png','tiff'] else {}
  if ext=='tiff':kwargs['pil_kwargs']={'compression':'tiff_lzw'}
  fig.savefig(F/(name+'.'+ext),**kwargs)
 fig.savefig(F/(name+'_preview.png'),dpi=150);plt.close(fig)
# Real video frames: seed/method and phase selection are explicit, no success-based selection.
phase={'T01':('pick_L',.65),'T02':('service1_L',.45),'T03':('pick_L',.95),'T04':('service2_L',.45),'T05':('transfer1',.50),'T06':('transfer2',.50),'T07':('transfer1',.50),'T08':('unload_pick_L',.70)}
fig,axes=plt.subplots(4,2,figsize=(7.2,8.85));fig.subplots_adjust(left=.015,right=.985,bottom=.045,top=.99,wspace=.045,hspace=.20)
frame_sources=[]
ffmpeg=Path(r'D:\ffmpeg\bin\ffmpeg.exe');ffmpeg=str(ffmpeg) if ffmpeg.exists() else 'ffmpeg'
for i,(task,ax) in enumerate(zip(tasks,axes.flat)):
 trial=E/f'{task}_100_nominal_full';plan=read(trial/'planning.json');node,fraction=phase[task];item=next(x for x in plan['schedule']['items'] if x['node_id']==node);t=item['start']+fraction*(item['finish']-item['start'])
 frame=F/(task+'_frame.png')
 if not frame.exists():subprocess.run([ffmpeg,'-v','error','-ss',str(t),'-i',str(trial/'execution.mp4'),'-frames:v','1',str(frame)],check=True)
 # The same crop removes the playback UI while retaining both full manipulators and table objects.
 im=Image.open(frame).crop((100,82,920,640));ax.imshow(im);ax.set_axis_off();ax.text(.5,-.015,f'({chr(97+i)}) {task}  {titles[i]}',ha='center',va='top',transform=ax.transAxes,fontsize=10)
 ax.text(.97,.97,f'{t:.2f} s',transform=ax.transAxes,ha='right',va='top',fontsize=10,color='#333333',bbox={'facecolor':'white','alpha':.8,'edgecolor':'none','pad':1})
 frame_sources.append({'task':task,'seed':100,'mode':'full','condition':'nominal','node':node,'within_action_fraction':fraction,'video_time_s':t,'crop_pixels':'100,82,920,640','video_sha256':hashlib.sha256((trial/'execution.mp4').read_bytes()).hexdigest()})
export(fig,'Figure9_task_scenes');csvout('figure9_frame_sources',frame_sources)
# Two complementary planning comparisons; repeated 5/5 nominal counts appear in Table 17.
fig,axes=plt.subplots(2,1,figsize=(7.2,5.35));fig.subplots_adjust(left=.10,right=.985,bottom=.13,top=.92,hspace=.70)
ax=axes[0];x=np.arange(8);width=.34
for offset,key,label,color in [(-width/2,'serial_window_s','Serial control','#bdc6cf'),(width/2,'full_window_s','Full method','#426f96')]:
 bars=ax.bar(x+offset,[r[key] for r in nominal],width,label=label,color=color,edgecolor='white',linewidth=.4)
 ax.bar_label(bars,fmt='%.0f',padding=2,fontsize=10)
ax.set_xticks(x,tasks);ax.set_ylabel('Scheduled window (s)');ax.set_ylim(0,65);tidy(ax);ax.legend(loc='lower right',bbox_to_anchor=(1,1.04),ncol=2,frameon=False);ax.text(.5,-.26,'(a) Fixed-skill schedule windows under nominal conditions',ha='center',transform=ax.transAxes,fontsize=10)
ax=axes[1];x=np.arange(4);width=.24
for j,(method,label,color) in enumerate(zip(methods,['Audit only','Field matching + compression','Full method'],['#bdc6cf','#83a894','#426f96'])):
 vals=[next(r['accepted'] for r in pc if r['profile']==p and r['method']==method) for p in profiles]
 bars=ax.bar(x+(j-1)*width,vals,width,label=label,color=color,edgecolor='white',linewidth=.4)
 for bar,v in zip(bars,vals):ax.text(bar.get_x()+bar.get_width()/2,max(v,.08)+.12,str(v),ha='center',fontsize=10)
ax.set_xticks(x,['No relations','Wrong state labels','Conservative order','Missing producer']);ax.set_ylabel('Accepted inputs (of 8)');ax.set_ylim(0,9.5);ax.set_yticks([0,2,4,6,8]);tidy(ax);ax.legend(loc='lower center',bbox_to_anchor=(.5,1.03),ncol=3,frameon=False);ax.text(.5,-.29,'(b) Same-input repair controls on constructed candidates',ha='center',transform=ax.transAxes,fontsize=10)
export(fig,'Figure10_planning_comparisons')
# Stress-condition outcomes: no error bars and explicit zero labels.
fig,axes=plt.subplots(2,1,figsize=(7.2,5.25),gridspec_kw={'height_ratios':[1.15,1]});fig.subplots_adjust(left=.10,right=.985,bottom=.13,top=.91,hspace=.75)
ax=axes[0];x=np.arange(8);width=.18;colors=['#4d7197','#c29a5a','#79a193','#9a87b2']
for j,(c,label,col) in enumerate(zip(conditions[1:],labels[1:],colors)):
 vals=[next(r['success'] for r in stress if r['task']==t and r['condition']==c) for t in tasks];bars=ax.bar(x+(j-1.5)*width,vals,width,label=label,color=col,edgecolor='white',linewidth=.3)
 for bar,v in zip(bars,vals):ax.text(bar.get_x()+bar.get_width()/2,max(v,.04)+.10,str(v),ha='center',fontsize=10)
ax.set_xticks(x,tasks);ax.set_ylim(0,6);ax.set_yticks(range(6));ax.set_ylabel('Completed runs (of 5)');tidy(ax);ax.legend(loc='lower center',bbox_to_anchor=(.5,1.03),ncol=4,frameon=False);ax.text(.5,-.28,'(a) One-factor stress tests using full scheduling',ha='center',transform=ax.transAxes,fontsize=10)
ax=axes[1];x=np.arange(4);bars=ax.bar(x,[f['count'] for f in failure],.57,color=['#7c9ab3','#8e85a2','#90ab9f','#c3ac82'],edgecolor='white');ax.bar_label(bars,padding=3,fontsize=9);ax.set_xticks(x,[f['first_failed_check'] for f in failure]);ax.set_ylabel('Failed runs');ax.set_ylim(0,30);tidy(ax);ax.text(.5,-.30,'(b) First failed check in each of the 56 failed runs',ha='center',transform=ax.transAxes,fontsize=10)
export(fig,'Figure11_execution_boundaries')
qa={'font':font,'error_bars':False,'panel_labels':'Centered below each panel, as requested','figure_width_mm':182.88,'exports':['SVG with editable text','PDF TrueType embedding','600 dpi PNG','600 dpi LZW TIFF'],'all_runs_included':True,'simulation_checks':{k:check[k] for k in ['total','integrity_valid','outcome_agreement']},'figure10_contract_refinement':'Use same-input planning controls in panel (b); all nominal completion counts are 5/5 and are retained in Table 17, avoiding a redundant panel.'}
(F/'figure_QA.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
