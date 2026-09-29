# ATG Repair 代码与项目主页

本仓库对应《面向双执行单元协同任务的可验证原子任务图关系修复与规划层并行规划》。当前论文稿为 v7.86（2026-09-29）；原规划归档仍标识为 v7.70，扩展 MuJoCo 实验归档仍标识为 v2。论文排版更新不改变实验归档版本。本仓库提供研究代码和数据，不宣称论文已被录用。

## 快速使用

需要 Python 3.11 或更新版本。当前实现和三组最新评价仅使用标准库，不需要模型 API、GPU 或机器人设备。在仓库根目录运行：

```sh
python tools/verify_archive.py
python tools/run_plan.py examples/tea_candidate.json --output local_runs/tea_result.json
python tools/check.py
python tools/serve.py
```

前三条分别校验归档、运行茶任务接口演示、运行58项实现检查及8项独立公共源核验器检查。茶任务是接口演示，持续时间为示意符号量，不能统计为新增实验。输出文件不得已存在。

最后一条启动主页：**http://127.0.0.1:8780/**。服务运行期间可以访问；按 Ctrl+C 停止。也可双击 `docs/index.html` 离线打开。端口冲突时可指定 `--port 8781`，但论文中的临时链接使用8780，需保持一致。

## 早期30次物理仿真研究

打开 **http://127.0.0.1:8780/#simulation**，查看MuJoCo双Panda机械臂的六段实际仿真录像，可切换并行分拣、共享工位、协同搬运及串行/本文调度。三类构造任务、五组初始位置、两种调度，共30次执行、15组配对条件；30次均通过预设完成判据及独立轨迹/事件复核。串行→本文执行窗口为24→12、40→28、22→17仿真秒。窗口由固定技能时长决定，不是实机测量，也不比较修复启发式优劣。

历史稿v7.74曾报告本组探索实验；当前论文的主要物理实验是下文的240次扩展批次。模型、物理接触、轨迹、代码和开发失败记录见[仿真复现说明](simulation/README.md)。此实验另需MuJoCo、NumPy、Pillow及FFmpeg，安装和运行命令见该说明；原v7.70规划归档不变。

## 实验动图

打开 **http://127.0.0.1:8780/#experiments**，可切换三组冻结实验记录的调度动画：受控饮品准备、公开并行装配，以及 ft06 资源定向对照。支持暂停、重新播放、倍速和拖动时间；B任务跨越L/R两条时间线，并在两个执行单元的实时状态中同步显示。各案例提供可独立打开的SVG动图下载。

动画按原始调度记录中的起止时间播放，时间轴为符号时间，不是机器人实拍，也不计为新增实验。受控饮品案例有6个节点，与论文的5节点茶任务示例不同。ft06两种方法使用共同时间轴；页面保留总体证据和负结果，不将单个实例的差异推为普遍优势。

重新生成命令：

```sh
python tools/build_replays.py
```

脚本先独立核验4份调度及相应图，公开案例还核验源规范，再导出网页数据、3个SVG动图和检查报告。冻结实验文件不变。完整来源及哈希见[实验动画说明](documentation/EXPERIMENT_REPLAYS.md)和 `docs/assets/data/replays.json`。

## 离线复算

```sh
cd reproduction
python reproduce_all.py results/new_run
```

结果目录必须不存在。脚本复算1024条内部对照、3944条公开工具存档评价、52条公开规范评价、8640条机制评价，并与归档逐项比较稳定结果。这些是设置记录数，不是独立任务数；耗时和冻结时间不要求一致。

历史 MILP 与计时依赖见 `reproduction/requirements-historical.txt`；对应重跑入口见[代码与证据映射](documentation/CODE_AND_EVIDENCE.md)。不要把历史耗时标成新版本测量。

## 从哪里读代码

- 正式接受入口：`reproduction/implementation_v7_70/atomic_task/pipeline.py` 的 `run_verified_atg`。
- 节点结构与原始类型检查：同目录 `schema.py`；关系修复：`optimization.py`；联合审计：`verification.py`；严格调度：`planning.py`。
- 同输入修复对照：`reproduction/repair_comparators.py` 与 `reproduce.py`。
- 独立检查：`reproduction/independent_audit.py` 与 `test_external_reference.py`。
- 公共规范适配：`reproduction/external_discrete.py`；有限机制枚举：`exhaustive_mechanism.py`。
- 已冻结实验的完整路径和表图对应关系见[代码与证据映射](documentation/CODE_AND_EVIDENCE.md)。

保留 `reproduction/` 原始相对路径和字节，避免破坏复算入口与哈希。`implementation_v7_69` 是历史版本，不是当前正式入口。

## 方法和证据边界

L、R是两个抽象基础执行单元，B同时占用L+R。四阶段顺序为状态闭合、同步配对、资源冲突定向、保守顺序压缩；仅试删有效 `E_order` 并重新审计。六项图审计及实际调度检查通过才接受，失败只输出诊断且不证明不可行。

受控160条记录的完整标签边F1由0.9018提高到0.9813，但共享压缩的简单对照达到0.9853；不能据此声称完整启发式普遍优于简单规则。6个公开资源任务的双执行单元投影中，完整方法相对共享压缩简单对照的逐实例完工时间平均降低25.7167%，不代表原始JSP最优值比较。公共工具任务上形式接受增加而参考边F1下降，负结果保留。

24份GPT-6候选来自同一方法知情会话，共254节点，原始计划全通过且净关系变化为0，不能包装成独立可核验API benchmark。公共规范候选由确定性适配得到。1728个三节点构造输入中，736个存在可行见证，完整方法接受720个，仍拒绝16个可行输入。

保证范围限于已表示的离散状态、容量1资源和执行单元占用，不包括漏标事实、连续碰撞、轨迹或硬件。

## 主页与后续发布

主页源文件位于 `docs/`，使用相对链接、无CDN字体、无分析追踪脚本。方法图取自当前Word内嵌图片，图1—4仅作EMF至PNG格式转换；没有重绘或替换论文原图。页面提供方法图切换、高清图查看、实验说明和完整复现包下载。

页面结构参考 Nerfies 与 Academic Project Page Template，来源见[说明](documentation/TEMPLATE_SOURCES.md)。作者代码采用 MIT；网页正文、布局和论文图采用 CC BY-SA 4.0；第三方数据和源文件保留原许可，详见[许可清单](LICENSES.md)。

部署步骤见[GitHub Pages说明](documentation/GITHUB_PAGES.md)。本地检查与复算命令不会上传数据。主库、Word内部稿和账户邮箱不进入此仓库；作者、机构、论文链接与引用条目将在核定后补充，复现代码可独立于未发表的稿件使用。

## 新增八类任务与物理压力实验

新增目录 [simulation_expanded](simulation_expanded/README.md) 保存240次实际MuJoCo运行、96组同输入规划设置、20段预选录像及独立状态核验。正常条件两种调度合计80/80完成，压力条件104/160完成；56次失败全部保留。当前v7.86论文的图9—11、表12—14报告这一批次；早期稿件的表号不同。旧30次探索和v7.70包不变。这些是物理仿真，不是实机结果，完整修复与共享压缩简单规则在本批接受输入上持平。
