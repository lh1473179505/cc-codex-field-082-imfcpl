# imfcpl

把已经入库的 IMF 节目包按新的分段策略写成一条 CompositionPlaylist。`probe` 已经能读 AssetMap、PackingList、CPL 虚拟轨和库房侧车。`compose` 还没有实现。

不要用 Docker，也不要引入 lxml、NumPy 或任何第三方 IMF / MXF 库。请复用 `imfcpl.am`、`imfcpl.pkl`、`imfcpl.cpl` 和 `imfcpl.descriptors`。编辑速率换算必须用整数算术。

## 命令

```
python -m imfcpl probe --package fixtures/show
python -m imfcpl compose \
  --package fixtures/show \
  --policy fixtures/policy.json \
  --output /tmp/imfcpl-new.xml \
  --report /tmp/imfcpl-report.json
```

规则见 `docs/compose-rules.md`，本仓库承认的 IMF 子集见 `docs/imf-subset.md`，报告字段见 `docs/report-schema.md`。
