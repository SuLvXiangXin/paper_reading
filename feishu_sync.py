#!/usr/bin/env python3
"""飞书知识库同步脚本 — 将本地 Markdown 知识库同步到飞书 Wiki

支持多领域分区同步：每个领域（如 vla/）在飞书中对应一个独立子树。

Usage:
    python feishu_sync.py              # 同步所有领域
    python feishu_sync.py --domain vla # 只同步指定领域
    python feishu_sync.py --rebuild    # 重建飞书结构（清空状态重新同步）
"""

import os
import sys
import json
import time
import re
import hashlib
import argparse
from pathlib import Path

import requests

# ─── 配置 ────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
KB_DIR = BASE_DIR / "knowledge_base"
SYNC_STATE_FILE = BASE_DIR / ".feishu_sync_state.json"

APP_ID = os.environ.get("FEISHU_APP_ID", "cli_a927261c6b78dcee")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
API_BASE = "https://open.feishu.cn"

SPACE_ID = "7615497891934751969"  # 科研
PARENT_NODE_TOKEN = "JC2dwDGtsiALc6k6niicI1gBnng"  # 项目

# 领域中文名映射
DOMAIN_TITLES = {
    "vla": "VLA（视觉-语言-动作模型）",
    "world_models": "World Models（世界模型）",
    "reward_learning": "Reward Learning（奖励学习）",
}

# 领域内标准子目录 → 飞书显示名
SUBDIR_TITLES = {
    "reports": "调研报告",
    "papers": "论文卡片",
    "methods": "方法分类",
    "components": "技术组件",
    "benchmarks": "评测体系",
    "tasks": "任务类型",
    "surveys": "论文调研",
}

# ─── API 工具 ────────────────────────────────────────────────────────────────

class FeishuClient:
    def __init__(self):
        self.token = None
        self.token_expires = 0

    def get_token(self):
        if self.token and time.time() < self.token_expires:
            return self.token
        resp = requests.post(
            f"{API_BASE}/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": APP_ID, "app_secret": APP_SECRET}
        )
        data = resp.json()
        self.token = data["tenant_access_token"]
        self.token_expires = time.time() + data.get("expire", 7200) - 60
        return self.token

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json"
        }

    def list_nodes(self, parent_node_token=None):
        """列出知识库节点"""
        params = {}
        if parent_node_token:
            params["parent_node_token"] = parent_node_token
        resp = requests.get(
            f"{API_BASE}/open-apis/wiki/v2/spaces/{SPACE_ID}/nodes",
            headers=self._headers(),
            params=params
        )
        data = resp.json()
        return data.get("data", {}).get("items", [])

    def create_node(self, title, parent_node_token, obj_type="docx"):
        """创建知识库节点"""
        resp = requests.post(
            f"{API_BASE}/open-apis/wiki/v2/spaces/{SPACE_ID}/nodes",
            headers=self._headers(),
            json={
                "obj_type": obj_type,
                "node_type": "origin",
                "parent_node_token": parent_node_token,
                "title": title
            }
        )
        data = resp.json()
        if data.get("code") != 0:
            print(f"  [错误] 创建节点 '{title}' 失败: {data.get('msg', data)}")
            return None
        node = data["data"]["node"]
        print(f"  [创建] {title} → node:{node['node_token']}")
        return node

    def _get_page_block_id(self, obj_token):
        """获取文档的 page block id（type=1），不存在则返回 obj_token"""
        resp = requests.get(
            f"{API_BASE}/open-apis/docx/v1/documents/{obj_token}/blocks",
            headers=self._headers(),
            params={"page_size": 50}
        )
        data = resp.json()
        if data.get("code") != 0:
            return obj_token
        for item in data.get("data", {}).get("items", []):
            if item.get("block_type") == 1:
                return item["block_id"]
        return obj_token

    def _count_direct_children(self, obj_token, page_block_id):
        """统计 page block 的直接子块数（需分页遍历所有 blocks）"""
        all_items = []
        page_token = None
        while True:
            params = {"page_size": 500}
            if page_token:
                params["page_token"] = page_token
            resp = requests.get(
                f"{API_BASE}/open-apis/docx/v1/documents/{obj_token}/blocks",
                headers=self._headers(), params=params
            )
            data = resp.json()
            if data.get("code") != 0:
                break
            all_items.extend(data.get("data", {}).get("items", []))
            if not data.get("data", {}).get("has_more"):
                break
            page_token = data["data"].get("page_token")
            time.sleep(0.1)
        return sum(1 for i in all_items if i.get("parent_id") == page_block_id)

    def _clear_doc_content(self, obj_token, page_block_id):
        """用 batch_delete 清空文档所有内容，循环直到无子块"""
        for _ in range(200):  # 最多 200 轮，防止死循环
            child_count = self._count_direct_children(obj_token, page_block_id)
            if child_count == 0:
                return True
            resp = requests.delete(
                f"{API_BASE}/open-apis/docx/v1/documents/{obj_token}/blocks/{page_block_id}/children/batch_delete",
                headers=self._headers(),
                json={"start_index": 0, "end_index": child_count}
            )
            try:
                result = resp.json()
            except Exception:
                return False
            if result.get("code") != 0:
                print(f"  [警告] 清空文档失败: {result.get('msg')}")
                return False
            time.sleep(0.3)
        return False

    def write_doc_markdown(self, obj_token, markdown_content):
        """写入 Markdown 内容：先清空文档所有内容，再写入新内容"""
        # 获取 page block id
        page_block_id = self._get_page_block_id(obj_token)

        # 用 batch_delete 清空所有子块（支持超过 500 块的大文档）
        self._clear_doc_content(obj_token, page_block_id)

        # 将 Markdown 转为飞书 blocks
        blocks = self._parse_markdown_to_feishu_blocks(markdown_content)

        # 分离表格占位和普通 blocks
        regular_blocks = []
        table_positions = []  # (insert_position, table_rows)

        for block in blocks:
            if isinstance(block, dict) and block.get("_type") == "table_placeholder":
                table_positions.append((len(regular_blocks), block["rows"]))
            else:
                regular_blocks.append(block)

        # 批量创建普通 blocks（飞书限制每次最多 50 个）
        if regular_blocks:
            BATCH_SIZE = 40
            for batch_start in range(0, len(regular_blocks), BATCH_SIZE):
                batch = regular_blocks[batch_start:batch_start + BATCH_SIZE]
                resp = requests.post(
                    f"{API_BASE}/open-apis/docx/v1/documents/{obj_token}/blocks/{page_block_id}/children",
                    headers=self._headers(),
                    json={"children": batch, "index": -1}
                )
                result = resp.json()
                if result.get("code") != 0:
                    print(f"  [警告] 写入内容失败 (batch {batch_start}): {result.get('msg')} {result.get('error', '')}")
                    return False
                time.sleep(0.2)

        # 创建表格（在对应位置插入）
        for offset, (insert_pos, rows) in enumerate(table_positions):
            self._create_table(obj_token, page_block_id, rows)
            time.sleep(0.3)

        return True

    def _create_table(self, doc_token, parent_block_id, rows):
        """创建飞书表格并填充内容。失败时回退到代码块。"""
        if not rows:
            return
        row_count = len(rows)
        col_count = max(len(r) for r in rows)

        # 创建表格 block
        resp = requests.post(
            f"{API_BASE}/open-apis/docx/v1/documents/{doc_token}/blocks/{parent_block_id}/children",
            headers=self._headers(),
            json={
                "children": [{
                    "block_type": 31,
                    "table": {
                        "property": {
                            "row_size": row_count,
                            "column_size": col_count
                        }
                    }
                }],
                "index": -1
            }
        )
        result = resp.json()
        if result.get("code") != 0:
            # 回退到代码块
            print(f"  [警告] 创建表格失败: {result.get('msg')}，回退到代码块")
            table_text = "\n".join("|".join(row) for row in rows)
            time.sleep(0.5)
            self._fallback_table_as_code(doc_token, parent_block_id, table_text)
            return

        # 获取表格 block 的子节点（行和单元格）
        table_block = result.get("data", {}).get("children", [{}])[0]
        table_block_id = table_block.get("block_id")
        if not table_block_id:
            return

        time.sleep(0.2)

        # 获取表格内部结构
        resp = requests.get(
            f"{API_BASE}/open-apis/docx/v1/documents/{doc_token}/blocks/{table_block_id}/children",
            headers=self._headers(),
            params={"page_size": 500}
        )
        children = resp.json().get("data", {}).get("items", [])

        # 表格结构: table → table_row (block_type 32) → table_cell (block_type 33)
        row_blocks = [c for c in children if c.get("block_type") == 32]

        for row_idx, row_block in enumerate(row_blocks):
            if row_idx >= len(rows):
                break

            # 获取该行的 cell blocks
            resp = requests.get(
                f"{API_BASE}/open-apis/docx/v1/documents/{doc_token}/blocks/{row_block['block_id']}/children",
                headers=self._headers(),
                params={"page_size": 500}
            )
            cell_blocks = resp.json().get("data", {}).get("items", [])
            cell_blocks = [c for c in cell_blocks if c.get("block_type") == 33]

            for col_idx, cell_block in enumerate(cell_blocks):
                if col_idx >= len(rows[row_idx]):
                    break

                cell_text = rows[row_idx][col_idx].strip()
                if not cell_text:
                    continue

                # 首行加粗（表头）
                is_header = (row_idx == 0)
                elements = self._make_text_elements(f"**{cell_text}**" if is_header else cell_text)

                # 向 cell 中添加段落
                resp = requests.post(
                    f"{API_BASE}/open-apis/docx/v1/documents/{doc_token}/blocks/{cell_block['block_id']}/children",
                    headers=self._headers(),
                    json={
                        "children": [{
                            "block_type": 2,
                            "text": {"elements": elements}
                        }],
                        "index": 0
                    }
                )
                if resp.json().get("code") != 0:
                    pass  # 静默失败，不影响整体

            time.sleep(0.1)

    def _fallback_table_as_code(self, doc_token, parent_block_id, table_text):
        """表格创建失败时回退为代码块。"""
        resp = requests.post(
            f"{API_BASE}/open-apis/docx/v1/documents/{doc_token}/blocks/{parent_block_id}/children",
            headers=self._headers(),
            json={
                "children": [self._make_code_block(table_text, "")],
                "index": -1
            }
        )
        try:
            result = resp.json()
            if result.get("code") != 0:
                print(f"  [警告] 代码块回退也失败: {result.get('msg')}")
        except Exception:
            print(f"  [警告] 代码块回退响应异常: status={resp.status_code}")

    def _parse_markdown_to_feishu_blocks(self, md_content):
        """将 Markdown 转为飞书文档 block 数组"""
        blocks = []
        lines = md_content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]

            # 空行跳过
            if not line.strip():
                i += 1
                continue

            # 代码块
            if line.strip().startswith('```'):
                lang = line.strip()[3:].strip()
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                i += 1  # skip closing ```
                blocks.append(self._make_code_block('\n'.join(code_lines), lang))
                continue

            # 标题
            heading_match = re.match(r'^(#{1,9})\s+(.+)', line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2)
                blocks.append(self._make_heading_block(text, level))
                i += 1
                continue

            # 无序列表
            if re.match(r'^[-*]\s+', line.strip()):
                text = re.sub(r'^[-*]\s+', '', line.strip())
                blocks.append(self._make_bullet_block(text))
                i += 1
                continue

            # 有序列表
            if re.match(r'^\d+\.\s+', line.strip()):
                text = re.sub(r'^\d+\.\s+', '', line.strip())
                blocks.append(self._make_ordered_block(text))
                i += 1
                continue

            # 分割线
            if re.match(r'^---+\s*$', line.strip()):
                blocks.append({"block_type": 22, "divider": {}})  # divider
                i += 1
                continue

            # 引用
            if line.strip().startswith('>'):
                text = line.strip()[1:].strip()
                blocks.append(self._make_quote_block(text))
                i += 1
                continue

            # 表格 — 创建表格占位，后续转为飞书原生表格
            if '|' in line and i + 1 < len(lines) and re.match(r'^[\s|:-]+$', lines[i + 1]):
                table_rows = []
                while i < len(lines) and '|' in lines[i]:
                    row_line = lines[i].strip().strip('|')
                    cells = [c.strip() for c in row_line.split('|')]
                    # 跳过分隔行（---|---|---）
                    if not re.match(r'^[\s:-]+$', row_line.replace('|', '')):
                        table_rows.append(cells)
                    i += 1
                if table_rows:
                    blocks.append({"_type": "table_placeholder", "rows": table_rows})
                continue

            # 普通段落
            blocks.append(self._make_paragraph_block(line.strip()))
            i += 1

        return blocks

    def _make_text_elements(self, text):
        """将含有 **bold** 和其他 Markdown 格式的文本转为 text elements"""
        elements = []
        parts = re.split(r'(\*\*[^*]+\*\*)', text)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                elements.append({
                    "text_run": {
                        "content": part[2:-2],
                        "text_element_style": {"bold": True}
                    }
                })
            elif part:
                code_parts = re.split(r'(`[^`]+`)', part)
                for cp in code_parts:
                    if cp.startswith('`') and cp.endswith('`'):
                        elements.append({
                            "text_run": {
                                "content": cp[1:-1],
                                "text_element_style": {"inline_code": True}
                            }
                        })
                    elif cp:
                        elements.append({
                            "text_run": {"content": cp}
                        })

        if not elements:
            elements.append({"text_run": {"content": text}})

        return elements

    def _make_paragraph_block(self, text):
        return {
            "block_type": 2,
            "text": {
                "elements": self._make_text_elements(text)
            }
        }

    def _make_heading_block(self, text, level):
        block_type = min(2 + level, 11)
        type_names = {3: "heading1", 4: "heading2", 5: "heading3", 6: "heading4",
                      7: "heading5", 8: "heading6", 9: "heading7", 10: "heading8", 11: "heading9"}
        name = type_names.get(block_type, "heading3")
        return {
            "block_type": block_type,
            name: {
                "elements": self._make_text_elements(text)
            }
        }

    def _make_bullet_block(self, text):
        return {
            "block_type": 12,
            "bullet": {
                "elements": self._make_text_elements(text)
            }
        }

    def _make_ordered_block(self, text):
        return {
            "block_type": 13,
            "ordered": {
                "elements": self._make_text_elements(text)
            }
        }

    def _make_code_block(self, code, language=""):
        # 飞书 text_run 限制约 500 字符，需要拆分
        MAX_LEN = 450
        elements = []
        for i in range(0, len(code), MAX_LEN):
            elements.append({"text_run": {"content": code[i:i+MAX_LEN]}})
        if not elements:
            elements = [{"text_run": {"content": " "}}]
        return {
            "block_type": 14,
            "code": {
                "elements": elements,
                "language": self._map_language(language)
            }
        }

    def _make_quote_block(self, text):
        return {
            "block_type": 15,
            "quote": {
                "elements": self._make_text_elements(text)
            }
        }

    def _map_language(self, lang):
        lang_map = {
            "python": 18, "bash": 7, "json": 16, "markdown": 20,
            "": 1,
        }
        return lang_map.get(lang.lower(), 1)

    def _reverse_map_language(self, lang_id):
        """飞书语言 ID → 语言名称。"""
        reverse_map = {18: "python", 7: "bash", 16: "json", 20: "markdown", 1: ""}
        return reverse_map.get(lang_id, "")

    def read_doc_blocks(self, obj_token):
        """读取飞书文档的所有 blocks。"""
        all_items = []
        page_token = None
        while True:
            params = {"page_size": 500}
            if page_token:
                params["page_token"] = page_token
            resp = requests.get(
                f"{API_BASE}/open-apis/docx/v1/documents/{obj_token}/blocks",
                headers=self._headers(),
                params=params
            )
            data = resp.json()
            if data.get("code") != 0:
                print(f"  [错误] 读取文档失败: {data.get('msg')}")
                return []
            items = data.get("data", {}).get("items", [])
            all_items.extend(items)
            if not data.get("data", {}).get("has_more"):
                break
            page_token = data["data"].get("page_token")
        return all_items

    def _extract_text_from_elements(self, elements):
        """将飞书 text elements 转换回 Markdown 文本。"""
        parts = []
        for elem in elements:
            text_run = elem.get("text_run", {})
            content = text_run.get("content", "")
            style = text_run.get("text_element_style", {})
            if style.get("bold"):
                content = f"**{content}**"
            if style.get("inline_code"):
                content = f"`{content}`"
            parts.append(content)
        return "".join(parts)

    def blocks_to_markdown(self, blocks):
        """将飞书 blocks 转换回 Markdown。"""
        lines = []
        type_names = {3: "heading1", 4: "heading2", 5: "heading3", 6: "heading4",
                      7: "heading5", 8: "heading6", 9: "heading7", 10: "heading8", 11: "heading9"}

        for block in blocks:
            bt = block.get("block_type")
            if bt == 1:  # page block
                continue
            elif bt == 2:  # paragraph
                elements = block.get("text", {}).get("elements", [])
                text = self._extract_text_from_elements(elements)
                lines.append(text)
                lines.append("")
            elif 3 <= bt <= 11:  # heading
                level = bt - 2
                name = type_names.get(bt, "heading3")
                elements = block.get(name, {}).get("elements", [])
                text = self._extract_text_from_elements(elements)
                lines.append(f"{'#' * level} {text}")
                lines.append("")
            elif bt == 12:  # bullet
                elements = block.get("bullet", {}).get("elements", [])
                text = self._extract_text_from_elements(elements)
                lines.append(f"- {text}")
            elif bt == 13:  # ordered
                elements = block.get("ordered", {}).get("elements", [])
                text = self._extract_text_from_elements(elements)
                lines.append(f"1. {text}")
            elif bt == 14:  # code
                code_data = block.get("code", {})
                elements = code_data.get("elements", [])
                code_text = self._extract_text_from_elements(elements)
                lang = self._reverse_map_language(code_data.get("language", 1))
                lines.append(f"```{lang}")
                lines.append(code_text)
                lines.append("```")
                lines.append("")
            elif bt == 15:  # quote
                elements = block.get("quote", {}).get("elements", [])
                text = self._extract_text_from_elements(elements)
                lines.append(f"> {text}")
                lines.append("")
            elif bt == 22:  # divider
                lines.append("---")
                lines.append("")
            elif bt == 31:  # table
                lines.append("[表格 — 需手动检查]")
                lines.append("")

        return "\n".join(lines)


# ─── 同步状态管理 ────────────────────────────────────────────────────────────

def load_sync_state():
    if SYNC_STATE_FILE.exists():
        return json.loads(SYNC_STATE_FILE.read_text())
    return {}

def save_sync_state(state):
    SYNC_STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def migrate_old_state(state: dict) -> dict:
    """将旧格式状态（扁平结构）迁移为新格式（领域分区结构）。

    旧格式: {root_node_token, subdirs: {methods: ...}, files: {papers/xxx: ...}}
    新格式: {root_node_token, domains: {vla: {node_token, subdirs, files}}}
    """
    if "domains" in state:
        return state  # 已是新格式

    if not state.get("subdirs"):
        return state  # 空状态，无需迁移

    print("[迁移] 检测到旧版同步状态，正在转换为新格式...")

    new_state = {
        "root_node_token": state.get("root_node_token"),
        "root_obj_token": state.get("root_obj_token"),
        "domains": {}
    }

    # 旧的 subdirs 和 files 全部属于 vla 领域
    # 但旧结构中它们直接在 root 下，新结构需要一个 vla 中间节点
    # 这个中间节点需要在飞书上创建，所以这里只做数据迁移标记
    new_state["domains"]["vla"] = {
        "node_token": None,  # 需要后续创建
        "obj_token": None,
        "subdirs": state.get("subdirs", {}),
        "files": state.get("files", {}),
        "_migrated_from_flat": True,  # 标记：子节点仍在旧位置
    }

    print("[迁移] 状态格式已更新。旧飞书节点保留不动，将在新 VLA 节点下重新创建。")
    return new_state


def _compute_file_hash(filepath: Path) -> str:
    """计算文件内容的 MD5 哈希。"""
    content = filepath.read_text(encoding="utf-8")
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def discover_domains() -> list[str]:
    """自动发现 knowledge_base/ 下的领域目录。"""
    domains = []
    for p in sorted(KB_DIR.iterdir()):
        if p.is_dir() and (p / "index.md").exists():
            domains.append(p.name)
    return domains


# ─── 同步逻辑 ────────────────────────────────────────────────────────────────

def sync_domain(client: FeishuClient, state: dict, domain: str, domain_dir: Path, force: bool = False):
    """同步一个领域的知识库到飞书。force=True 时跳过 hash 对比，强制全量同步。"""
    domain_title = DOMAIN_TITLES.get(domain, domain)
    domain_state = state["domains"].get(domain, {})

    root_node_token = state["root_node_token"]

    # 1. 确保领域节点存在
    if not domain_state.get("node_token") or domain_state.get("_migrated_from_flat"):
        # 需要创建领域节点
        existing = client.list_nodes(root_node_token)
        found = False
        for node in existing:
            if node["title"] == domain_title:
                domain_state["node_token"] = node["node_token"]
                domain_state["obj_token"] = node["obj_token"]
                found = True
                print(f"  [已存在] {domain_title}")
                break

        if not found:
            node = client.create_node(domain_title, root_node_token)
            if not node:
                print(f"  [错误] 无法创建领域节点: {domain_title}")
                return
            domain_state["node_token"] = node["node_token"]
            domain_state["obj_token"] = node["obj_token"]
            time.sleep(0.3)

        # 清除迁移标记——旧子节点不迁移，在新节点下全部重建
        if domain_state.get("_migrated_from_flat"):
            domain_state.pop("_migrated_from_flat", None)
            domain_state["subdirs"] = {}
            domain_state["files"] = {}

    # 2. 写入领域总览页
    index_path = domain_dir / "index.md"
    if index_path.exists():
        index_hash = _compute_file_hash(index_path)
        if force or index_hash != domain_state.get("index_hash"):
            content = index_path.read_text(encoding="utf-8")
            client.write_doc_markdown(domain_state["obj_token"], content)
            domain_state["index_hash"] = index_hash
            print(f"  [更新] {domain_title} 总览页")
            time.sleep(0.3)
        else:
            print(f"  [跳过] {domain_title} 总览页未变更")

    # 3. 创建子目录节点
    if "subdirs" not in domain_state:
        domain_state["subdirs"] = {}
    if "files" not in domain_state:
        domain_state["files"] = {}

    # 扫描实际存在的子目录
    actual_subdirs = {}
    for p in sorted(domain_dir.iterdir()):
        if p.is_dir() and p.name in SUBDIR_TITLES:
            actual_subdirs[p.name] = SUBDIR_TITLES[p.name]

    for subdir, title in actual_subdirs.items():
        if subdir not in domain_state["subdirs"]:
            # 检查飞书是否已存在
            existing = client.list_nodes(domain_state["node_token"])
            found = False
            for node in existing:
                if node["title"] == title:
                    domain_state["subdirs"][subdir] = {
                        "node_token": node["node_token"],
                        "obj_token": node["obj_token"]
                    }
                    print(f"    [已存在] {title}")
                    found = True
                    break

            if not found:
                node = client.create_node(title, domain_state["node_token"])
                if node:
                    domain_state["subdirs"][subdir] = {
                        "node_token": node["node_token"],
                        "obj_token": node["obj_token"]
                    }
                time.sleep(0.3)
        else:
            print(f"    [跳过] {title} (已存在)")

    # 4. 同步子目录 index
    for subdir, info in domain_state["subdirs"].items():
        idx_path = domain_dir / subdir / "index.md"
        if idx_path.exists():
            idx_hash = _compute_file_hash(idx_path)
            if force or idx_hash != info.get("index_hash"):
                content = idx_path.read_text(encoding="utf-8")
                client.write_doc_markdown(info["obj_token"], content)
                info["index_hash"] = idx_hash
                print(f"    [更新] {actual_subdirs.get(subdir, subdir)} 概览页")
                time.sleep(0.3)
            else:
                print(f"    [跳过] {actual_subdirs.get(subdir, subdir)} 概览页未变更")

    # 5. 同步所有子文件
    for subdir in actual_subdirs:
        subdir_path = domain_dir / subdir
        parent_info = domain_state["subdirs"].get(subdir)
        if not parent_info:
            continue

        for md_file in sorted(subdir_path.glob("*.md")):
            if md_file.name == "index.md":
                continue

            file_key = f"{subdir}/{md_file.name}"
            file_hash = _compute_file_hash(md_file)

            # 提取标题
            content = md_file.read_text(encoding="utf-8")
            title_match = re.match(r'^#\s+(.+)', content)
            title = title_match.group(1) if title_match else md_file.stem
            if len(title) > 50:
                title = title[:47] + "..."

            if file_key not in domain_state["files"]:
                # 新文件：创建节点并写入
                node = client.create_node(title, parent_info["node_token"])
                if node:
                    domain_state["files"][file_key] = {
                        "node_token": node["node_token"],
                        "obj_token": node["obj_token"],
                        "title": title,
                        "last_sync_hash": file_hash
                    }
                    client.write_doc_markdown(node["obj_token"], content)
                    print(f"    [同步] {file_key}")
                time.sleep(0.5)
            else:
                file_info = domain_state["files"][file_key]
                if not force and file_hash == file_info.get("last_sync_hash"):
                    print(f"    [跳过] {file_key} 未变更")
                    continue
                # 内容变更：重写
                client.write_doc_markdown(file_info["obj_token"], content)
                file_info["last_sync_hash"] = file_hash
                print(f"    [更新] {file_key}")
                time.sleep(0.3)

    # 6. 检测已删除的文件
    local_files = set()
    for subdir in actual_subdirs:
        for md_file in (domain_dir / subdir).glob("*.md"):
            if md_file.name != "index.md":
                local_files.add(f"{subdir}/{md_file.name}")
    for file_key in list(domain_state.get("files", {}).keys()):
        if file_key not in local_files:
            print(f"    [警告] {file_key} 本地已删除（飞书节点保留，使用 --rebuild 清理）")

    state["domains"][domain] = domain_state


def sync_to_feishu(target_domain: str = None, force: bool = False):
    """将本地知识库同步到飞书。force=True 时跳过 hash 对比，强制全量同步。"""
    client = FeishuClient()
    state = load_sync_state()
    state = migrate_old_state(state)

    print("=" * 60)
    print("飞书知识库同步")
    print("=" * 60)

    # 1. 确保 Paper Reading 根节点存在
    root_node_token = state.get("root_node_token")
    root_obj_token = state.get("root_obj_token")

    if not root_node_token:
        print("\n1. 创建/查找 Paper Reading 根节点...")
        existing = client.list_nodes(PARENT_NODE_TOKEN)
        for node in existing:
            if node["title"] == "Paper Reading":
                root_node_token = node["node_token"]
                root_obj_token = node["obj_token"]
                print(f"  [已存在] Paper Reading → node:{root_node_token}")
                break

        if not root_node_token:
            node = client.create_node("Paper Reading", PARENT_NODE_TOKEN)
            if not node:
                print("创建根节点失败！")
                return
            root_node_token = node["node_token"]
            root_obj_token = node["obj_token"]

        state["root_node_token"] = root_node_token
        state["root_obj_token"] = root_obj_token
    else:
        print(f"\n1. Paper Reading 根节点: {root_node_token}")

    # 2. 写入总览 Dashboard
    print("\n2. 同步总览 Dashboard...")
    dashboard_path = KB_DIR / "index.md"
    if dashboard_path.exists():
        dash_hash = _compute_file_hash(dashboard_path)
        if force or dash_hash != state.get("dashboard_hash"):
            content = dashboard_path.read_text(encoding="utf-8")
            client.write_doc_markdown(root_obj_token, content)
            state["dashboard_hash"] = dash_hash
            print("  [更新] 总览 Dashboard 已更新")
        else:
            print("  [跳过] 总览 Dashboard 未变更")

    # 3. 同步各领域
    if "domains" not in state:
        state["domains"] = {}

    domains = discover_domains()
    if target_domain:
        if target_domain not in domains:
            print(f"\n[错误] 领域 '{target_domain}' 不存在。可用领域: {', '.join(domains)}")
            return
        domains = [target_domain]

    print(f"\n3. 同步领域: {', '.join(domains)}")

    for domain in domains:
        domain_dir = KB_DIR / domain
        print(f"\n{'─'*40}")
        print(f"领域: {DOMAIN_TITLES.get(domain, domain)}")
        print(f"{'─'*40}")
        sync_domain(client, state, domain, domain_dir, force=force)
        save_sync_state(state)

    save_sync_state(state)

    # 统计
    total_files = sum(len(d.get("files", {})) for d in state["domains"].values())
    total_subdirs = sum(len(d.get("subdirs", {})) for d in state["domains"].values())

    print(f"\n{'='*60}")
    print("同步完成!")
    print(f"飞书知识库: 科研 → 项目 → Paper Reading")
    print(f"领域数: {len(state['domains'])}")
    print(f"子目录数: {total_subdirs}")
    print(f"文件数: {total_files}")
    print(f"{'='*60}")


def sync_from_feishu(target_domain: str = None, force: bool = False):
    """从飞书反向同步到本地知识库。"""
    client = FeishuClient()
    state = load_sync_state()
    state = migrate_old_state(state)

    if not state.get("domains"):
        print("无同步状态，请先运行正向同步 (python feishu_sync.py)")
        return

    print("=" * 60)
    print("从飞书反向同步到本地")
    print("=" * 60)

    domains_to_sync = {}
    if target_domain:
        if target_domain not in state.get("domains", {}):
            print(f"\n[错误] 领域 '{target_domain}' 无同步记录")
            return
        domains_to_sync = {target_domain: state["domains"][target_domain]}
    else:
        domains_to_sync = state.get("domains", {})

    for domain, domain_state in domains_to_sync.items():
        domain_dir = KB_DIR / domain
        domain_title = DOMAIN_TITLES.get(domain, domain)
        print(f"\n{'─'*40}")
        print(f"领域: {domain_title}")
        print(f"{'─'*40}")

        # 1. 同步领域总览页
        obj_token = domain_state.get("obj_token")
        if obj_token:
            blocks = client.read_doc_blocks(obj_token)
            if blocks:
                md = client.blocks_to_markdown(blocks)
                index_path = domain_dir / "index.md"
                index_path.parent.mkdir(parents=True, exist_ok=True)

                # 冲突检测
                if not force and index_path.exists():
                    local_hash = _compute_file_hash(index_path)
                    if local_hash != domain_state.get("index_hash"):
                        print(f"  [冲突] index.md 本地有未同步修改，跳过 (使用 --force 覆盖)")
                    else:
                        index_path.write_text(md, encoding="utf-8")
                        print(f"  [同步] index.md")
                else:
                    index_path.write_text(md, encoding="utf-8")
                    print(f"  [同步] index.md")
            time.sleep(0.3)

        # 2. 同步子目录 index
        for subdir, info in domain_state.get("subdirs", {}).items():
            obj_token = info.get("obj_token")
            if not obj_token:
                continue
            blocks = client.read_doc_blocks(obj_token)
            if blocks:
                md = client.blocks_to_markdown(blocks)
                idx_path = domain_dir / subdir / "index.md"
                idx_path.parent.mkdir(parents=True, exist_ok=True)

                if not force and idx_path.exists():
                    local_hash = _compute_file_hash(idx_path)
                    if local_hash != info.get("index_hash"):
                        print(f"  [冲突] {subdir}/index.md 本地有未同步修改，跳过")
                        continue

                idx_path.write_text(md, encoding="utf-8")
                print(f"  [同步] {subdir}/index.md")
            time.sleep(0.3)

        # 3. 同步详细文件
        for file_key, info in domain_state.get("files", {}).items():
            obj_token = info.get("obj_token")
            if not obj_token:
                continue
            blocks = client.read_doc_blocks(obj_token)
            if blocks:
                md = client.blocks_to_markdown(blocks)
                file_path = domain_dir / file_key
                file_path.parent.mkdir(parents=True, exist_ok=True)

                if not force and file_path.exists():
                    local_hash = _compute_file_hash(file_path)
                    if local_hash != info.get("last_sync_hash"):
                        print(f"  [冲突] {file_key} 本地有未同步修改，跳过")
                        continue

                file_path.write_text(md, encoding="utf-8")
                print(f"  [同步] {file_key}")
            time.sleep(0.3)

    print(f"\n{'='*60}")
    print("反向同步完成!")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="飞书知识库同步")
    parser.add_argument("direction", nargs="?", default="push", choices=["push", "pull"],
                        help="push=本地→飞书 (默认), pull=飞书→本地")
    parser.add_argument("--domain", default=None, help="只同步指定领域")
    parser.add_argument("--force", action="store_true", help="强制同步（push: 跳过 hash 对比; pull: 覆盖本地修改）")
    parser.add_argument("--rebuild", action="store_true", help="重建飞书结构（清空本地状态）")
    args = parser.parse_args()

    if args.rebuild:
        print("⚠️  重建模式：将清空本地同步状态，在飞书上重新创建所有节点。")
        print("   旧的飞书节点不会被删除，需要手动清理。")
        confirm = input("   确认继续? (y/N): ")
        if confirm.lower() != 'y':
            print("已取消。")
            sys.exit(0)
        # 清空状态
        SYNC_STATE_FILE.write_text("{}")
        print("   已清空同步状态。\n")

    if args.direction == "pull":
        sync_from_feishu(target_domain=args.domain, force=args.force)
    else:
        sync_to_feishu(target_domain=args.domain, force=args.force)
