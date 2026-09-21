# ATG v7_70 随稿数据与代码

对应中文版 v7_70。根目录当前实现位于 implementation_v7_70，历史版本保留。实验不连接模型 API 或机器人。

## 一条命令离线复现

Python 3.11+，当前三组评价仅使用标准库。在本包根目录运行：

```
python reproduce_all.py results/new_run
```

输出目录必须不存在。脚本复现并逐项核对1024条内部对照、3944条公开工具存档评价、52条公开规范评价及8640条机制评价（1728输入×5设置）。这些是设置记录数，不是独立任务数。稳定结果与归档比较；冻结时间和机器耗时不要求一致。

## 检查与文件映射

```
python -m unittest discover -s implementation_v7_70/tests -v
python -m unittest test_external_reference -v
```

第一条须设置PYTHONPATH为implementation_v7_70，或进入该目录运行 python -m unittest discover -s tests -v。实现检查58项，公共源核验器回归8项。

- 表13、14：results/fair_comparison；inputs为冻结输入；external为固定提交的工具任务参考和候选存档。
- 表15、16：results/external_discrete_run01；sources为AssemblyGrid固定公开提交及OR-Library数据；external_discrete_protocol.md为冻结协议。6/10配方、1个官方OR规范测试、6个JSP投影分别统计，排除项完整保留。
- 三节点完整枚举：results/exhaustive_run01。736/1728输入有可行见证；完整方法和带无环筛选的简单组合均接受720，仍拒绝16个可行输入；所有方法零错误接受。不能把这些构造用例称为独立工业任务。
- 表1—7：dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907。
- 原始24份GPT-6会话候选：analysis_outputs/gpt6_current_session_planning_20260917_v1，方法知情单会话、首轮冻结，不能称独立API benchmark。
- 表8—12、图7—8：analysis_outputs/experiment_expansion_v7_63_20260917。历史MILP和计时依赖见requirements-historical.txt；在该目录运行 python rerun_in_new_directory.py --name reproduction_run01。历史耗时不重标为当前版本测量。

## 证据边界与归档

160份受控输入中，简单组合加共享压缩的边F1与加速比略高于完整方法。公开工具存档的参考边F1下降。这些负结果均保留。

六个双执行单元JSP投影中完整方法均更短，逐实例平均降低25.7167%，成对差异仅来自资源关系。投影增加两个通用执行单元，不与原JSP最优值比较。AssemblyGrid仅验证离散投影保留的材料、先后和协作约束，不运行原几何、技能与运输仿真。参考从公开源读取，候选由确定性适配生成；并非新增自然语言模型错误样本。

来源、哈希、许可及原实例归属保留在sources和external；本包不包含EndNote主库、Word内部稿、账户或认证数据。MANIFEST_SHA256.json校验固定归档文件。本地随稿归档已完成，公开持久标识须由发布平台分配，不预填虚构URL或DOI。
