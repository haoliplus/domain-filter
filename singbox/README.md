# sing-box-geosite

在links.txt添加规则集，自动生成 sing-box Source Format。fork后自己添加想要转换的规则集，请生成token填写到仓库设置里让GitHub Actions有权限修改你的仓库

规则集源文件写法eg:

```json
{
  "tag": "geosite-wechat",
  "type": "remote",
  "format": "source",
  "url": "https://raw.githubusercontent.com/Toperlock/sing-box-geosite/main/wechat.json",
  "download_detour": "auto"
}
```

# 致谢（排名不分先后）

[@izumiChan16](https://github.com/izumiChan16)

[@ifaintad](https://github.com/ifaintad)

[@NobyDa](https://github.com/NobyDa)

[@blackmatrix7](https://github.com/blackmatrix7)

[@DivineEngine](https://github.com/DivineEngine)

## 仓库内 Surge 规则的原生版本

`singbox/surge/` 对应本仓库 `surge/` 中的 17 个集合，保留原匹配内容，
与原有 `singbox/rule/` 的其他上游集合分开。生成器不下载规则。
修改 Surge 源后，现有 Config Update 工作流会重新生成这些 JSON；也可运行：

```sh
python3 -m unittest discover -s singbox -p 'test_convert_surge.py' -v
python3 singbox/convert_surge.py
```

客户端直接使用远程 source rule-set，例如：

```json
{
  "type": "remote",
  "tag": "surge-ai",
  "format": "source",
  "url": "https://raw.githubusercontent.com/haoliplus/domain-filter/main/singbox/surge/ai.json",
  "download_detour": "direct",
  "update_interval": "1d"
}
```

使用支持 version 3 的 sing-box（已用 1.14.2 校验）。域名、IP 和进程条件分开为
OR 规则；CIDR 正规化；`no-resolve` 不写入原生规则集。
`Download.list` 的 URL-REGEX 与 `apple.list` 的 USER-AGENT 没有原生路由等价项，
明确跳过并输出警告，不扩大成域名匹配。`manifest.json` 记录源文件、SHA-256、
条目数和跳过行；遇到其他未知类型或选项则终止生成。

GitHub 的 schedule 只在默认分支执行；若默认分支不是 main，main 上的工作流
仍可由 push 或手动执行触发，不能据此假定每天自动更新。
