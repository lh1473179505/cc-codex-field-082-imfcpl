# compose 规则

默认策略见 `fixtures/policy.json`。输入是一个 IMF 节目包目录和这份策略，输出是一条新的 CompositionPlaylist 和一份报告。不要改源 CPL，也不要改 AssetMap / PackingList。

## 输入

- `--package` 指向含 `ASSETMAP.xml` 的目录。源 CPL 的文件名由策略 `source_cpl` 给出，相对该目录。
- 策略 `composition_edit_rate` 是输出 CPL 的编辑速率，写成 `[分子, 分母]`。
- `video_track_id` 指定要保留的画面轨。
- `audio_select` 给出 `language` 与 `mca_tag`（例如 `51` 表示 5.1，`st` 表示立体声）。在源 CPL 的音频轨里挑一条：先跟 `descriptors.json` 里对应 `TrackFileId` 的 `language` 和 `mca_tag` 精确匹配；多条命中时取源 CPL 中先出现的那条。一条都没有则退出 1，`decision` 为 `reject`，`reason_codes` 含 `audio_not_found`。
- `include_subtitle` 为 `false` 时不要把字幕轨写进新 CPL，并在报告的 `dropped_tracks` 里列出被丢掉的 `track_id`。为 `true` 时按语言挑选，规则与音频相同（字段是 `subtitle_select.language`）。
- `head_trim_eu` / `tail_trim_eu` 是按**源 CPL 的编辑速率**计算的片头、片尾裁切，作用在源时间线（含 RepeatCount 展开之后）的两端。它们不是 bumper 的时长。
- `bumper` 若存在，要在裁切后的节目前面再插一段垫乐/垫画。`video_track_file_id` 和 `audio_track_file_id` 指向包里已登记的资产。bumper 资源的 `EditRate` 与 `IntrinsicDuration` 以 `descriptors.json` 为准；`entry_point` 由策略给出，缺省 0。`source_duration` 缺省为 `IntrinsicDuration - entry_point`。bumper 本身不再做 head/tail trim。

## 换算

把某个资源上的时长 `N`（资源编辑单位）换到合成编辑速率 `Rc = nc/dc`，资源速率 `Rr = nr/dr`：

```
N * nc * dr  /  (dc * nr)
```

结果必须是整数。若除不尽：

- `non_integer_convert` 为 `reject`：退出 1，`reason_codes` 含 `non_integer_rate`，并写明哪个资源。
- 为 `snap_floor`：向零取整（只在隐藏用例里出现，公开夹具应当除尽）。

公开夹具里，`24000/1001` 的画面帧和 `48000/1` 的音频样点满足 `1` 帧 = `2002` 样点。`24/1` 的垫画 `1001` 帧换到 `24000/1001` 应得到正好 `1000` 个合成编辑单位。不要用近似的 23.976 或 0.0417 这类小数去做。

## 裁切与 RepeatCount

先在源时间线上把每个资源按 `SourceDuration * RepeatCount` 展开成一段占用，再从整条序列的头、尾减去 `head_trim_eu`、`tail_trim_eu`（先把这两个值换到该序列资源自己的编辑单位；换算规则同上，除不尽则按 `non_integer_convert`）。然后再把仍留在窗口里的片段收成输出 Resource：

- 若裁切只碰到某资源的若干完整重复，留下的 `RepeatCount` 是剩余次数，`EntryPoint` / `SourceDuration` 不变。
- 若裁切切进某一次重复的内部，把这次重复收成 `RepeatCount = 1`，并改 `EntryPoint` 或 `SourceDuration`。不要把一次不完整的重复再和其他完整重复合并成一个更大的 `RepeatCount`。
- 被完全裁掉的资源不要写进输出。
- 不要把源时间线上本来独立的两个 Resource 合并成一个，即使它们指向同一 `TrackFileId`。
- 一条源 Resource 如果裁切后仍是连续的一段，就还是一条输出 Resource，只改入点和时长；不要因为画面上后面还有 ident 就把音频文件拆成两段。

头尾裁切之后，各保留轨在合成编辑单位上的时长必须相等。不等则按 `duration_mismatch` 处理：公开策略是 `reject`。

## bumper 与段落

输出只写一个 `Segment`。`ResourceList` 的顺序是：bumper（若有），然后裁切后仍保留的源资源，保持它们在源序列里的相对顺序。bumper 的合成时长必须在画面和音频之间对齐；对不齐则 `reject`，`reason_codes` 含 `bumper_mismatch`。

新 CPL 的 `Id`、唯一 `Segment` 的 `Id`、各序列 `Id`、各 Resource `Id` 使用策略里的 `new_cpl_id`、`new_segment_id`、`new_sequence_ids`、`new_resource_ids`。缺了必要的 Id 才允许新生成 UUID，公开夹具里这些字段都给全了。源资产的 `TrackFileId` 必须原样保留，禁止给 essence 换新 Id。

`new_resource_ids` 的键：

- `bumper_video` / `bumper_audio`
- `main_video`：源主画面那一条裁切后的 Resource
- `ident_video`：片尾 ident 裁切后若还在，用这个 Id
- `main_audio`：选中的源音频裁切后的那一条 Resource

## Marker

`markers[].offset_eu` 是输出合成时间线上的偏移，单位是 `composition_edit_rate`，范围必须满足 `0 <= offset_eu < total_duration_eu`。越界则退出 1，`reason_codes` 含 `marker_out_of_range`。输出 CPL 在根下写本仓库子集认可的 `MarkerList` / `Marker`（`Label`、`Offset`、`Annotation`），不要另造一种只存在于报告里的标记。

公开策略里 FFOA 在 `1000`（垫画结束、节目第一帧），LFOA 在 `1887`（合成总长 `1888` 的最后一帧）。

## 空隙与重叠

同一条虚拟轨上，按合成编辑单位排列资源后不得有空隙或重叠。出现空隙且 `gap_mode` 为 `reject`，或出现重叠且 `overlap_mode` 为 `reject`，则退出 1。

## 写出的 CPL

- 命名空间与源 CPL 相同。画面 / 音频序列分别使用 `MainImageSequence` / `MainAudioSequence`。
- `EditRate` 为策略中的合成速率，写成 `分子 分母`。
- `ContentTitle`、`ContentKind`、`Issuer`、`Creator`、`IssueDate`、`ApplicationIdentificationList` 按策略填写。
- 每个 Resource 都要写出 `EditRate`、`IntrinsicDuration`、`EntryPoint`、`SourceDuration`、`RepeatCount`、`TrackFileId`。`IntrinsicDuration` 来自 `descriptors.json`（不是裁切后的源时长）。
- 不要把被丢掉的音频或字幕轨写进去。

## 退出码

- 成功写出 CPL 和完整报告：退出 0，`decision` 为 `ok`。
- 策略无法满足（选不中音轨、除不尽、时长对不齐、标记越界、空隙或重叠）：退出 1，`decision` 为 `reject`，报告仍要写出，且 `reason_codes` 非空。
- AssetMap / CPL / 策略 / 侧车无法解析：退出 2。此时可以不写报告。
