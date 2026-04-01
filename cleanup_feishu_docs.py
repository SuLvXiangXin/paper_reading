#!/usr/bin/env python3
"""正确清空飞书文档：batch_delete 需精确指定子块数量。"""

import json, requests, time

import os
APP_ID = os.environ.get("FEISHU_APP_ID", "cli_a927261c6b78dcee")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
API_BASE = "https://open.feishu.cn"

_token = None
_token_expires = 0

def get_token():
    global _token, _token_expires
    if _token and time.time() < _token_expires:
        return _token
    resp = requests.post(f"{API_BASE}/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET})
    data = resp.json()
    _token = data["tenant_access_token"]
    _token_expires = time.time() + data.get("expire", 7200) - 60
    return _token


def h():
    return {"Authorization": f"Bearer {get_token()}", "Content-Type": "application/json"}


def get_direct_children_count(obj_token, page_block_id):
    """获取 page block 的直接子块数（需要分页遍历所有 blocks）"""
    all_items = []
    page_token = None
    while True:
        params = {"page_size": 500}
        if page_token:
            params["page_token"] = page_token
        resp = requests.get(f"{API_BASE}/open-apis/docx/v1/documents/{obj_token}/blocks",
            headers=h(), params=params)
        data = resp.json()
        if data.get("code") != 0:
            return 0
        items = data.get("data", {}).get("items", [])
        all_items.extend(items)
        if not data.get("data", {}).get("has_more"):
            break
        page_token = data["data"].get("page_token")
        time.sleep(0.2)
    return sum(1 for i in all_items if i.get("parent_id") == page_block_id)


def get_page_block_id(obj_token):
    """获取文档的 page block id"""
    resp = requests.get(f"{API_BASE}/open-apis/docx/v1/documents/{obj_token}/blocks",
        headers=h(), params={"page_size": 50})
    data = resp.json()
    if data.get("code") != 0:
        return obj_token  # fallback: page block id == obj_token for docx
    for item in data.get("data", {}).get("items", []):
        if item.get("block_type") == 1:
            return item["block_id"]
    return obj_token


def clear_doc(obj_token, doc_name):
    """完全清空文档内容，循环直到没有子块"""
    page_block_id = get_page_block_id(obj_token)
    rounds = 0
    total_deleted = 0

    while True:
        # 获取当前直接子块数
        child_count = get_direct_children_count(obj_token, page_block_id)
        if child_count == 0:
            break

        # batch_delete 精确删除所有子块
        resp = requests.delete(
            f"{API_BASE}/open-apis/docx/v1/documents/{obj_token}/blocks/{page_block_id}/children/batch_delete",
            headers=h(),
            json={"start_index": 0, "end_index": child_count}
        )
        try:
            result = resp.json()
        except Exception:
            print(f"    ⚠ 响应解析失败: {resp.status_code}")
            break

        if result.get("code") != 0:
            print(f"    ⚠ batch_delete 失败: {result.get('msg')} (child_count={child_count})")
            break

        total_deleted += child_count
        rounds += 1
        time.sleep(0.5)

        if rounds > 100:
            print(f"    ⚠ 超过最大轮数，强制退出")
            break

    # 最终验证
    time.sleep(0.5)
    remaining = get_direct_children_count(obj_token, page_block_id)
    status = "✓ 已清空" if remaining == 0 else f"⚠ 仍有 {remaining} 个子块"
    print(f"  {doc_name}: {rounds} 轮，删除 {total_deleted} 个子块；{status}")
    return remaining == 0


def main():
    with open(".feishu_sync_state.json") as f:
        state = json.load(f)

    docs = [("Dashboard", state["root_obj_token"])]
    for domain_name, domain in state["domains"].items():
        docs.append((f"{domain_name}/index", domain["obj_token"]))
        for subdir, info in domain["subdirs"].items():
            docs.append((f"{domain_name}/{subdir}/index", info["obj_token"]))
        for fkey, finfo in domain["files"].items():
            docs.append((f"{domain_name}/{fkey}", finfo["obj_token"]))

    print(f"共 {len(docs)} 个文档需要清空\n")
    success = 0
    partial = 0
    for doc_name, obj_token in docs:
        ok = clear_doc(obj_token, doc_name)
        if ok:
            success += 1
        else:
            partial += 1

    print(f"\n清空完成: {success} 个文档完全清空, {partial} 个仍有残留")
    if partial == 0:
        print("\n✓ 所有文档已清空，可以运行：python feishu_sync.py --force")


if __name__ == "__main__":
    main()
