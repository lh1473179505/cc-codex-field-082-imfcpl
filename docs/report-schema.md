# 报告 schema

成功或 `reject` 时都要写这份 JSON。字段如下。

| 字段 | 类型 | 含义 |
|---|---|---|
| package | string | 包目录 |
| policy | string | 策略路径 |
| decision | string | `ok` 或 `reject` |
| reason_codes | string[] | 失败原因；成功时为空数组 |
| source_cpl_id | string | 源 CPL 的 Id |
| output_cpl_id | string | 新 CPL 的 Id |
| composition_edit_rate | [int, int] | 输出编辑速率 |
| total_duration_eu | int | 输出总时长，合成编辑单位 |
| bumper_duration_eu | int | 垫画时长，没有垫画则为 0 |
| head_trim_eu | int | |
| tail_trim_eu | int | |
| selected_audio_track_id | string 或 null | |
| dropped_tracks | string[] | 未写入输出 CPL 的源 `TrackId` |
| markers | object[] | `label_kind`、`offset_eu`、`annotation` |
| resources | object[] | 见下表，按输出时间线顺序 |

`resources` 中每一项：

| 字段 | 类型 | 含义 |
|---|---|---|
| track_kind | string | `video` 或 `audio` |
| track_file_id | string | |
| resource_id | string | 输出 Resource 的 Id |
| edit_rate | [int, int] | 该资源自己的编辑速率 |
| entry_point | int | |
| source_duration | int | 一次播放的源时长 |
| repeat_count | int | |
| composition_start_eu | int | 该资源在输出合成时间线上的起点 |
| composition_duration_eu | int | 该资源占用的合成时长（已计入 RepeatCount） |
