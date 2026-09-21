# ATG v7_69 随稿数据与代码

对应中文版 v7_69。根目录实现是收紧数值输出检查的 v7_69；历史实验保留各自版本，禁止把旧墙钟计时解释为新版本测量。本包没有在线模型调用或机器人控制依赖。

## 快速复现

Python 3.11+。第4.8节评价只用标准库。在本目录运行：

```
python reproduce.py results/new_run
python test_new_evidence_v69.py
```

`results/new_run`必须不存在，脚本拒绝覆盖。冻结的256份输入×4设置产生1024条内部评价，986份外部候选×4设置产生3944条评价，不是4968个独立任务。全部接受输出另经独立图和调度核验。

实现测试请进入`implementation_v7_69`后运行`python -m unittest discover -s tests -v`，共55项；接口与证据检查另6项。`verification`记录本轮通过日志及结果比对。既有三设置共3726条结果完全不变；其他984条派生评价也逐项回放核验。

## 论文与文件映射

- 表13、表14及第4.8节：`results/fair_comparison`含全部图、严格调度、失败诊断、逐记录CSV和汇总；`inputs`为冻结候选及单独评分参考。新增简单组合与完整方法共用压缩、审计及调度实现。
- 24份GPT-6原始候选及冻结协议：`analysis_outputs/gpt6_current_session_planning_20260917_v1`。任务与候选来自方法知情会话，不称独立工艺金标准或可复现API benchmark。
- 表8—12、图7—8的派生实验、计时与MILP：`analysis_outputs/experiment_expansion_v7_63_20260917`。保存输入、完整账本、计划、求解原始结果和下界。另建Python环境按`requirements-historical.txt`安装依赖后，在该目录运行`python rerun_in_new_directory.py --name reproduction_run01`。只在新目录运行，计时随机器负载变化。
- 表1—7及历史主实验：`dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907`。记录160条四拓扑时长变体的原始任务、图、调度、诊断及主表；补充目录的`historical_replay`保存跨版本数值核验。

## 来源与解释

外部工具任务/参考/存档输出来自GNN4TaskPlan仓库固定提交f1486690f4fa00030bc7035f0dcc41904889aa2c；来源哈希、许可及原文件在`external`。保留所有存档及适配失败。未执行存档模型API；不将工具参数一致性解释为机器人状态、资源或B占用语义正确。

共享压缩后简单组合平均加速比1.2619、完整方法1.2535；公开工具输出的平均参考边F1下降。这些结果必须与接受率一起报告，不选择性隐藏。独立机器人工艺参考与隔离自然候选仍未建立。

`MANIFEST_SHA256.json`校验所有文件。包内不含用户EndNote库、Word内部处理稿或账户信息；这是随稿本地补充包，未宣称已有公共托管链接或DOI。
