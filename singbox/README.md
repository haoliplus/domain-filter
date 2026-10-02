# sing-box 规则集

规则内容完全由本仓库维护，工作流不再下载第三方规则列表。

- `surge/`：仓库根目录下的自维护 Surge 源规则。
- `singbox/surge/`：由上述 17 份源文件转换的原生 JSON 与 manifest，请修改源文件后生成。
- `singbox/rule/`：已有原生规则文件，保留现有远程链接，由本仓库直接维护；
  工作流不再从外部覆盖这些文件。若修改 JSON 并继续提供对应 SRS，也需同步编译该 SRS。

## 生成与发布

修改根目录 `surge/` 的规则并推送到 main 后，Config Update 工作流运行转换测试、
生成 `singbox/surge/*.json`，有变化时自动提交并推送生成文件。
已移除定时拉取、`links.txt` 和旧下载脚本，只使用 Python 标准库转换仓库内文件。
本地运行：

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

## 历史来源致谢

既有规则与旧转换实现参考过以下项目，现已停止自动同步其规则：

- [izumiChan16](https://github.com/izumiChan16)
- [ifaintad](https://github.com/ifaintad)
- [NobyDa](https://github.com/NobyDa)
- [blackmatrix7](https://github.com/blackmatrix7)
- [DivineEngine](https://github.com/DivineEngine)
