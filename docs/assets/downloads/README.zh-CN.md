# ATG Repair 代码与项目主页

本仓库对应《面向双执行单元协同任务的可验证原子任务图关系修复与规划层并行规划》。实验冻结版本为 v7.70；v7.71 仅在论文摘要末尾补入本地主页链接。本仓库当前仅在本地 Git 中准备，未上传 GitHub。

## 快速使用

需要 Python 3.11 或更新版本。当前实现和三组最新评价仅使用标准库，不需要模型 API、GPU 或机器人设备。在仓库根目录运行：

```sh
python tools/verify_archive.py
python tools/run_plan.py examples/tea_candidate.json --output local_runs/tea_result.json
python tools/check.py
python tools/serve.py
```

前三条分别校验归档、运行茶任务接口演示、运行58项实现检查及8项独立公共源核验器检查。茶任务是接口演示，持续时间为示意符号量，不能统计为新增实验。输出文件不得已存在。

最后一条启动主页：**http://127.0.0.1:8765/**。服务运行期间可以访问；按 Ctrl+C 停止。也可双击 `docs/index.html` 离线打开。端口冲突时可指定 `--port 8766`，但论文中的临时链接使用8765，需保持一致。

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

本轮不创建远端、不上传、不启用GitHub Pages。后续发布步骤见[GitHub Pages说明](documentation/GITHUB_PAGES.md)。主库、Word内部稿和账户邮箱不进入此仓库；作者、机构、论文链接与引用条目应在核定后填写，不预置虚构信息。
