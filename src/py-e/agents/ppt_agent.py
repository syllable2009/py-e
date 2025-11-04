import tempfile
import os
import uuid
import requests
from typing import Dict, Any, Optional, Tuple, List
import pypandoc
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse
import random
from datetime import datetime
import re


class PPTGenerationAgent:

    # pandoc 在将 Markdown 转换为 PowerPoint（.pptx）时，会根据 Markdown 的结构自动选择对应的 slide layout（版式）。
    # 它依赖的是 英文版式名称（layout name），而不是中文或其他语言。
    @staticmethod
    def convert_md_to_ppt(md_content: str, file_info: Dict[str, Any]) -> bytes:
        '''
        md转化成ppt
        :param md_content:
        :param file_info:
        :return:
        '''
        # 临时目录，模板和生成的文件都存放在临时目录里
        temp_dir = Path(tempfile.gettempdir())
        # 从kconf中获取模板list
        template_list: List[str] = file_info.get("template_list", [])
        template_path: str = None
        if template_list is not None and template_list:
            template_url: str = random.choice(template_list)
            if template_url:
                path = urlparse(template_url).path
                p = PurePosixPath(path)
                print(temp_dir)
                target_path = os.path.join(temp_dir, p.name)
                if os.path.isfile(target_path):
                    template_path = target_path
                else:
                    with open(target_path, 'wb') as f:
                        # 下载模板存储，可以复用
                        f.write()
                        template_path = target_path
        # 构造请求对象
        title = file_info.get("title", "ppt")
        author = file_info.get("author", "mario团队")
        date = file_info.get("date", "2025-03-08")
        extra_args: List[str] = [
            # '--slide-level=1', # 指定哪一级标题开始新幻灯片（默认 2）
            # '--extract-media=./media', # 提取嵌入的图片到目录（对 PPTX 通常不需要）
            # '--standalone', # 生成完整文档（PPTX 默认就是 standalone）
            # "--toc",  # 生成目录幻灯片（需模板支持，且 pandoc 会尝试用 Title and Content 布局）
            # "--toc-depth=1",  # 目录包含的标题层级（默认 3）
            "-f", "markdown+smart+fenced_divs+emoji+footnotes",
            # 启用智能引号（“”‘’）,支持 :smile: 表情,支持 ::: columns 分栏（用于 Two Content）,
            "-M", f"title={title}",
            "-M", f"author={author}",
            "-M", f"date={date}",
            # "--verbose"  # 显示详细日志（包括 layout 匹配信息）

        ]
        if template_path and os.path.exists(template_path):
            extra_args.extend(['--reference-doc', str(template_path)])
        else:
            extra_args.extend(['--reference-doc', '/Users/jiaxiaopeng/ppt/6666.potx'])

        pptx_name = f"{uuid.uuid4().hex}.pptx";
        out_temp_path = os.path.join(temp_dir, pptx_name)
        try:
            pypandoc.convert_text(
                source=md_content,
                to='pptx',  # to='pptx' 时必须提供 outputfile，因为 .pptx 是二进制文件，无法以字符串形式返回。
                format='markdown',
                outputfile=out_temp_path,
                extra_args=extra_args,
                encoding='utf-8'
            )
            if out_temp_path and os.path.exists(out_temp_path):
                return Path(out_temp_path).read_bytes()

        except Exception as e:
            print(e)
            raise RuntimeError(f"Pandoc conversion ppt failed: {e}")
            return None
        finally:
            # 清理临时文件，只清理最终生成的文件，模板不清理
            if os.path.exists(out_temp_path):
                os.unlink(out_temp_path)


def extract_first_h1(md_content: str) -> str | None:
    # 1. 尝试从 YAML front matter 提取 title
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', md_content, re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        title_match = re.search(r'^title:\s*(.+)$', yaml_content, re.MULTILINE | re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            # 去除可能的引号（YAML 支持带引号的字符串）
            title = re.sub(r'^["\'](.*)["\']$', r'\1', title)
            if title:
                return title

    # 2. 尝试提取第一个 # 标题
    h1_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()

    # 3. 尝试提取第一个 ## 标题（可选，根据需求开启）
    h2_match = re.search(r'^##\s+(.+)$', md_content, re.MULTILINE)
    if h2_match:
        return h2_match.group(1).strip()
    return "无标题"


if __name__ == '__main__':
    md_path = '/Users/jiaxiaopeng/ppt/slides.md'
    markdown_text = ""
    # with open(md_path, 'r', encoding='utf-8') as f:
    #     markdown_text = f.read()
    # print(markdown_text)
    # content = Path(md_path).read_text(encoding='utf-8')

    # print(content)
    text = '''---
title: 全球老龄研究
author: 研究院
---

# 引言

## 全球老龄化趋势

- 联合国数据显示，全球65岁以上人口占比已从1950年的5%上升至2025年的约10%。
- 发达国家老龄化程度更高：日本、意大利、德国等国65岁以上人口占比超过20%。
- 中国自2000年进入老龄化社会，预计2025年65岁以上人口将突破2.1亿，占比约15%。

## 老龄化成因

- **生育率持续下降**：全球总和生育率从1950年的5.0降至2025年的约2.3。
- **人均寿命延长**：医疗进步与公共卫生改善使全球平均预期寿命达73岁（2025年）。
- **人口结构惯性**：婴儿潮一代集中步入老年，加速老龄化进程。

# 数据

## 主要国家/地区老龄化指标（2025年预测）

| 国家/地区 | 65岁以上人口占比 | 老年抚养比 |
|-----------|------------------|------------|
| 日本      | 29.5%            | 52         |
| 意大利    | 24.1%            | 41         |
| 中国      | 15.2%            | 22         |
| 美国      | 17.3%            | 27         |
| 印度      | 7.8%             | 12         |

## 中国老龄化关键数据

- **老年人口总量**：约2.12亿（65岁及以上）
- **高龄老人（80+）**：超3200万，年均增长5%
- **城乡差异**：农村老龄化率（17.1%）高于城市（14.3%）
- **独居/空巢老人**：占比超50%，心理健康与照护需求突出

# 挑战

## 社会保障压力加剧

- 养老金支付压力增大，部分省份已出现当期赤字。
- 医疗支出快速增长：老年人人均医疗费用为青壮年的3–5倍。
- 长期护理服务体系尚未健全，专业护理人员缺口超千万。

## 劳动力供给萎缩

- 劳动年龄人口（15–64岁）自2013年起持续下降。
- 2025年预计劳动人口减少至9.6亿，较峰值减少约8000万。
- “未富先老”问题在部分中西部地区尤为突出。

## 家庭结构与代际关系变化

- 核心家庭与独居老人增多，传统家庭养老功能弱化。
- “4-2-1”家庭结构普遍，中年一代养老负担沉重。
- 老年数字鸿沟加剧社会隔离风险。

# 对策

## 政策层面

- **延迟退休**：渐进式推行法定退休年龄调整。
- **养老金制度改革**：推动多层次养老保险体系（基本+企业年金+个人储蓄）。
- **长期护理保险试点扩面**：2025年覆盖全国主要城市。

## 科技赋能

- 推广智慧养老：智能穿戴、远程医疗、AI陪护等技术应用。
- 建设适老化数字基础设施，弥合“银色数字鸿沟”。
- 利用大数据预测区域养老需求，优化资源配置。

## 社会参与

- 鼓励“积极老龄化”：支持老年人再就业、志愿服务与终身学习。
- 发展社区嵌入式养老模式，构建15分钟养老服务圈。
- 强化家庭支持政策：税收优惠、照护假、喘息服务等。

# 展望

## 人口结构新常态

- 老龄化不可逆转，将成为21世纪中国基本国情。
- 到2035年，中国将进入重度老龄化社会（65岁以上人口占比超20%）。
- “长寿经济”崛起，银发产业市场规模预计2025年突破12万亿元。

## 可持续发展路径

- 构建“全龄友好型社会”：从城市规划到公共服务均需考虑老年需求。
- 推动代际融合：通过教育、社区活动促进老少共融。
- 国际合作应对共性挑战：共享经验、技术与政策工具。

## 结语

> “老龄化不是危机，而是转型的契机。”  
> —— 通过制度创新、科技支撑与社会共识，我们有能力将老龄化挑战转化为高质量发展的新动力。'''
    now = datetime.now()
    h1 = extract_first_h1(text)
    file_info: Dict[str, Any] = {
        # "template_path": None,
        "filename": None,
        "title": h1,
        "author": "Mario团队",
        "date": now.strftime("%Y-%m-%d"),
    }
    ppt_bytes: bytes = PPTGenerationAgent.convert_md_to_ppt(text, file_info)

    if ppt_bytes is not None:
        out_temp_path = '/Users/jiaxiaopeng/ppt/final.pptx'
        Path(out_temp_path).write_bytes(ppt_bytes)
        print("save to %s" % out_temp_path)
    # out_temp_path = '/Users/jiaxiaopeng/ppt/ccc.html'
    # html = md_to_revealjs_html(text, out_temp_path)
    # Path(out_temp_path).write_text(html, encoding="utf-8")
    # print("success")
