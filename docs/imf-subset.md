# 本仓库使用的 IMF 子集

本工具只处理母版车间这一条合成链路里会碰到的 IMF 子集，不是完整的 ST 2067 实现。不要去拉外部规范库或第三方 IMF 工具。

## 文件

- `ASSETMAP.xml`：SMPTE ST 429-9 AssetMap。命名空间 `http://www.smpte-ra.org/schemas/429-9/2007/AM`。`PackingList` 元素为 `true` 的那一项指向 PackingList。
- `PACKINGLIST.xml`：SMPTE ST 429-8 PackingList。命名空间 `http://www.smpte-ra.org/schemas/429-8/2007/PKL`。
- `CPL_*.xml`：SMPTE ST 2067-3 CompositionPlaylist。命名空间 `http://www.smpte-ra.org/schemas/2067-3/2016`。虚拟轨序列元素使用 ST 2067-2 命名空间 `http://www.smpte-ra.org/schemas/2067-2/2016`，本子集只认 `MainImageSequence`、`MainAudioSequence`、`MainSubtitleSequence`。这些序列内部的 `Id`、`TrackId`、`ResourceList`、`Resource` 仍在 CPL 命名空间。
- `descriptors.json`：库房侧车，和 `ASSETMAP.xml` 放在同一目录。它不是 IMF 资产，不必写进 AssetMap。键是资产 UUID（与 PKL / `TrackFileId` 一致），值给出 `kind`、`edit_rate`、`intrinsic_duration`、可选的 `language`、`mca_tag`、`channels`。本夹具不提供真实 MXF essence，合成只依据 CPL 和这份侧车。

## 编辑速率

`EditRate` 写成 `分子 分母`，例如 `24000 1001` 或 `48000 1`。时长、入点、源时长都以该资源自己的编辑单位计数。合成时间线的编辑速率由策略给出，换算必须用整数交叉相乘，不能先变成浮点秒再四舍五入。

## Resource 字段

- `IntrinsicDuration`：essence 固有时长，单位是该资源 `EditRate`。
- `EntryPoint`：从 essence 开头算起的入点，缺省 0。
- `SourceDuration`：一次播放取出的时长；缺省为 `IntrinsicDuration - EntryPoint`。必须满足 `EntryPoint + SourceDuration <= IntrinsicDuration`。
- `RepeatCount`：把上面这段源时长连续重复多少次，缺省 1。该资源在所属序列里占用的时长是 `SourceDuration * RepeatCount`，仍以资源编辑单位计。
- `TrackFileId`：指向 PKL 资产 Id。

## 本子集不做的事

不解析或重写 Partition、Index、RIP，不计算 MXF Hash，不处理 Encrypted Essence，不处理 CPL 数字签名，不展开 IMF sidecar 以外的 EssenceDescriptorList。
