# surge-module-bundle

把 iPhone / MacBook Air 上正在用的一批 Surge 模块**合并成单个 `.sgmodule`**，每天自动跟随上游更新。

## 订阅地址（Surge → 模块 → 从 URL 安装）

```text
https://raw.githubusercontent.com/liuweiqiang0523/surge-module-bundle/main/EgernSync.sgmodule
```

## 为什么合并

原先把 Egern 里启用的 26 个模块逐个装到 Surge，设备一多就要重复点几十次。这里把它们合成一个：

- `sources.txt`：模块来源清单（一行一个 URL）
- `build.py`：抓取 → 解析 `[Script]/[URL Rewrite]/[Header Rewrite]/[Body Rewrite]/[Map Local]/[Rule]/[MITM]` → 合并 → 写出 `EgernSync.sgmodule`
- `.github/workflows/build.yml`：每天 03:00（北京时间）自动重建，内容有变化才提交

## 维护要点

| 想做的事 | 怎么做 |
|---|---|
| 加一个模块 | 往 `sources.txt` 加一行 URL，提交；构建会自动合并 |
| 删一个模块 | 从 `sources.txt` 删掉那行，提交 |
| 上游改域名/脚本地址 | 在 `build.py` 里加改写规则（例：`kelee.one` → `hub.kelee.one`），已内置 |
| 客户端更新 | Surge → 模块 → 「全部更新」 |

## 生成规则（踩过的坑）

- 模块里的 `{{{参数}}}` 必须在合并前用该模块 `#!arguments=` 的默认值替换，否则整份模块失效
- `%APPEND%` / `%INSERT%` / `%REPLACE%` 是模块指令，不是主机名；不清理会让 Surge 报「MITM 主机名列表包含无法匹配任何主机的无效条目」
- 合并后无法单独开关某个模块；需要细粒度控制时拆成多个包

## 说明

仓库公开是为了让 Surge 能免 token 直接拉取；内容只有公开第三方模块的合并结果，不含任何凭据。
