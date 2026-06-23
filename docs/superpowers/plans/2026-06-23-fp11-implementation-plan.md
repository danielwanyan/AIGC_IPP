# FP-11 商品未物理出镜豁免规则实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement FP-11 anti-false-positive rule across all rule and prompt files, then push to GitHub.

**Architecture:** Update 5 files with consistent FP-11 rule definition, following the existing pattern of FP-01 through FP-10. Each file update is self-contained and testable.

**Tech Stack:** Plain text files (rules and prompts), git for version control

---

## File Structure

| File | Responsibility | Change Type |
|------|----------------|-------------|
| `rules/rules_text.txt` | Master rule definition document | Modify - add FP-11 rule, update version, update flow, add example |
| `prompts/reviewer_system_prompt.txt` | Expert reviewer system prompt | Modify - add FP-11 to core principles and FP list |
| `prompts/chief_judge_system_prompt.txt` | Chief judge system prompt | Modify - add FP-11 to reminders and FP review table |
| `prompts/reviewer_user_prompt.txt` | Expert reviewer user prompt | Modify - add FP-11 to reminders |
| `prompts/chief_judge_user_prompt.txt` | Chief judge user prompt | Modify - add FP-11 to reminders |

---

### Task 1: Update rules/rules_text.txt - Version Info and Change Log

**Files:**
- Modify: `rules/rules_text.txt:1-10` (version info section)
- Modify: `rules/rules_text.txt:772-783` (change log section)

- [ ] **Step 1: Update version info (lines 4-9)**

Replace:
```
- 当前版本：2026-06-22-v7
- 上次更新：2026-06-22
- 更新内容：支持挂车商品全量图片对比（JSON 数组格式），新增 FP-10（product_category 元数据仅用于豁免判断，禁止基于元数据与图片不一致判定 IPP）防误判规则
```

With:
```
- 当前版本：2026-06-23-v8
- 上次更新：2026-06-23
- 更新内容：新增 FP-11（商品未物理出镜豁免）防误判规则，明确有讲品但商品未以实物形式物理展示（仅屏幕/截图/口头）不算 IPP，更新判定流程和示例
```

- [ ] **Step 2: Add change log entry at the top of the change log table (before line 776)**

Add this row as the first row in the table (after the header):
```
| 2026-06-23-v8 | 2026-06-23 | 新增 FP-11（商品未物理出镜豁免）防误判规则，明确有讲品但商品未以实物形式物理展示（仅屏幕/截图/口头）不算 IPP，更新判定流程和示例 |
```

- [ ] **Step 3: Verify changes**

Read the file to confirm version info and change log are correctly updated.

- [ ] **Step 4: Commit**

```bash
cd /Users/bytedance/Desktop/AIGC_IPP
git add rules/rules_text.txt
git commit -m "feat(rules): update version to v8 and add change log for FP-11"
```

---

### Task 2: Update rules/rules_text.txt - 判定流程 Step 2

**Files:**
- Modify: `rules/rules_text.txt:79-100` (判定流程 section)

- [ ] **Step 1: Update Step 2 in the判定流程 (lines 86-88)**

Replace:
```
Step 2: 商品对比（视频帧商品 vs 挂车商品全量图片）
    ├─ 视频帧商品与任意一张商品图片一致 → 不命中（no_hit）
    └─ 视频帧商品与所有商品图片都不一致 → Step 3
```

With:
```
Step 2: 商品对比（视频帧商品 vs 挂车商品全量图片）
    ├─ 首先检查：视频帧中是否有挂车商品的物理实物展示？
    │   ├─ 无物理展示（仅屏幕/截图/口头）→ 不命中（no_hit，FP-11）
    │   └─ 有物理展示 → 继续对比
    ├─ 视频帧商品与任意一张商品图片一致 → 不命中（no_hit）
    └─ 视频帧商品与所有商品图片都不一致 → Step 3
```

- [ ] **Step 2: Verify changes**

Read the file to confirm the判定流程 is correctly updated.

- [ ] **Step 3: Commit**

```bash
cd /Users/bytedance/Desktop/AIGC_IPP
git add rules/rules_text.txt
git commit -m "feat(rules): update 判定流程 Step 2 with FP-11 physical presence check"
```

---

### Task 3: Update rules/rules_text.txt - Add FP-11 Rule Definition

**Files:**
- Modify: `rules/rules_text.txt:378-379` (after FP-10, before 豁免规则 section)

- [ ] **Step 1: Insert FP-11 rule after FP-10 (after line 378, before the `---` separator)**

Insert this content:

```
---

### 规则 FP-11：商品未物理出镜豁免
### Rule FP-11: Product Not Physically Shown Exemption

**问题场景**：ASR/OCR 有商品推广内容，但视频帧中挂车商品仅出现在手机屏幕、电脑截图中，或仅口头提及，商品本身没有以实物形式物理出镜。这种情况不属于"货不对板"，因为根本没有展示商品可供对比。

**判定规则**：
- ✅ 如果 ASR/OCR 有推广，但视频帧中**未出现挂车商品的物理实物展示** → **豁免（no_hit）**
- ✅ 物理实物展示定义：商品以真实实物形式出现在视频中（手持、摆放、穿戴等）
- ❌ 以下情况**不属于**物理实物展示：
  - 商品仅出现在手机屏幕、电脑屏幕、电视屏幕等电子屏幕中
  - 商品仅出现在截图、图片展示中
  - 仅口头提及商品，没有任何视觉展示
- ❌ 如果视频帧中出现了**其他商品的物理展示**（与挂车商品不同）→ 仍需判断是否不一致（不适用 FP-11）

**判断流程**：
```
ASR/OCR 有推广？
    ├─ 否 → no_hit
    └─ 是 → 视频帧中是否有挂车商品的物理实物展示？
        ├─ 无（仅屏幕/截图/口头）→ no_hit（FP-11）
        └─ 有 → 对比该实物与挂车商品图片
            ├─ 一致 → no_hit
            └─ 不一致 → 进入豁免检查
```

**示例**：
- 挂车商品：淋巴排毒补充剂（瓶装）
- ASR："Buy this lymphatic drainage supplement!"
- 视频帧：主播讲解 + 医疗解剖动画，没有出现任何补充剂瓶子/包装
- **判定**：no_hit（FP-11），商品未物理出镜，无法对比是否一致
```

- [ ] **Step 2: Verify changes**

Read the file to confirm FP-11 rule is correctly inserted after FP-10.

- [ ] **Step 3: Commit**

```bash
cd /Users/bytedance/Desktop/AIGC_IPP
git add rules/rules_text.txt
git commit -m "feat(rules): add FP-11 product not physically shown exemption rule"
```

---

### Task 4: Update rules/rules_text.txt - 判定逻辑总结和示例

**Files:**
- Modify: `rules/rules_text.txt:480-491` (判定逻辑总结 table)
- Modify: `rules/rules_text.txt:660-661` (before 防误判示例 section)

- [ ] **Step 1: Add row to判定逻辑总结 table (after line 489, before the `---` separator)**

Add this row to the table:
```
| 有推广 + 商品未物理出镜（仅屏幕/截图/口头） | no_hit | 商品未物理展示，无法对比（FP-11） |
```

- [ ] **Step 2: Add判定示例 8 before 防误判示例 section (after line 660, before the `## 防误判示例` header)**

Insert this content:

```
### 示例 8：不命中（商品未物理出镜，FP-11）

**输入**：
- aigc_video_id: 12345
- ASR: "Buy this lymphatic drainage supplement! Only $29.99!"
- 视频帧：医疗解剖动画 + 穿白大褂的人讲解，没有出现任何补充剂瓶子/包装
- 挂车商品图片：瓶装补充剂
- product_category: "Dietary Supplements"

**判定**：no_hit
**exemption_check**:
  - category_type: normal
  - is_exempted: true
  - exemption_reason: "Product not physically shown exemption"
**理由**：Product is promoted in ASR but not physically shown in any video frames (only AIGC-generated medical imagery). Cannot determine if product is consistent or not. FP-11 applies.

---
```

- [ ] **Step 3: Verify changes**

Read the file to confirm the summary table and example are correctly added.

- [ ] **Step 4: Commit**

```bash
cd /Users/bytedance/Desktop/AIGC_IPP
git add rules/rules_text.txt
git commit -m "feat(rules): add FP-11 to logic summary table and example 8"
```

---

### Task 5: Update prompts/reviewer_system_prompt.txt

**Files:**
- Modify: `prompts/reviewer_system_prompt.txt:43-58` (防误判原则 section)
- Modify: `prompts/reviewer_system_prompt.txt:84-96` (防误判规则 table in output format section)

- [ ] **Step 1: Add FP-11 to 防误判原则 bullet list (after line 55)**

After the line:
```
- **`{{product_category}}` 元数据与图片显示的商品不一致（FP-10）**
```

Add:
```
- **商品未物理出镜不算 IPP（FP-11）**：有讲品但商品未以实物形式物理展示（仅屏幕/截图/口头），不算货不对板
```

- [ ] **Step 2: Add new section "5.1 商品物理出镜检查" after 防误判原则 (after line 58, before `## 判定规则`)**

Insert:
```
### 5.1 商品物理出镜检查
- 在进行商品对比之前，必须先检查视频帧中是否有挂车商品的**物理实物展示**
- 如果 ASR/OCR 有推广，但商品未物理出镜（仅屏幕/截图/口头提及）→ 判定为 no_hit（FP-11）
- 物理实物展示：商品以真实实物形式出现在视频中（手持、摆放、穿戴等）
- 非物理展示：仅出现在电子屏幕中、仅截图展示、仅口头提及
- 如果视频中出现了其他商品的物理展示（与挂车商品不同）→ 仍需判断是否不一致（FP-11 不适用）
```

- [ ] **Step 3: Add FP-11 to the防误判规则 table in the output format section (after line 97, the FP-10 row)**

Add this row to the table:
```
| FP-11 | 商品未物理出镜豁免（仅屏幕/截图/口头提及不算展示，有讲品但无实物展示不算 IPP） |
```

Wait, actually looking at the file structure, the FP rules table is in the chief_judge_system_prompt.txt, not reviewer_system_prompt.txt. Let me check - the reviewer_system_prompt.txt has the rules inline in section 5, and the chief_judge_system_prompt.txt has the table. So for reviewer_system_prompt.txt, I just need to add FP-11 to the bullet list and add section 5.1.

Actually, re-reading the reviewer_system_prompt.txt, lines 84-96 are the field说明 for the output format, not the FP rules table. The FP rules table is in chief_judge_system_prompt.txt. So for reviewer_system_prompt.txt:

- [ ] **Step 3 (corrected): Verify no FP table in reviewer_system_prompt.txt**

The reviewer_system_prompt.txt doesn't have an FP rules table - that's only in chief_judge_system_prompt.txt. So no change needed here for the table.

- [ ] **Step 4: Verify all changes to reviewer_system_prompt.txt**

Read the file to confirm FP-11 is correctly added to the bullet list and section 5.1 is added.

- [ ] **Step 5: Commit**

```bash
cd /Users/bytedance/Desktop/AIGC_IPP
git add prompts/reviewer_system_prompt.txt
git commit -m "feat(prompts): add FP-11 to reviewer system prompt"
```

---

### Task 6: Update prompts/chief_judge_system_prompt.txt

**Files:**
- Modify: `prompts/chief_judge_system_prompt.txt:5-11` (重要提醒 section)
- Modify: `prompts/chief_judge_system_prompt.txt:84-98` (防误判规则审查 table)

- [ ] **Step 1: Update 重要提醒 section (lines 5-7)**

Replace:
```
• **重点审查防误判规则（FP-01至FP-10）的应用情况**
• **特别关注 FP-08（纯颜色差异豁免）、FP-09（小物件/装饰品忽略）和 FP-10（product_category 仅用于豁免判断）的正确应用**
```

With:
```
• **重点审查防误判规则（FP-01至FP-11）的应用情况**
• **特别关注 FP-08（纯颜色差异豁免）、FP-09（小物件/装饰品忽略）、FP-10（product_category 仅用于豁免判断）和 FP-11（商品未物理出镜豁免）的正确应用**
```

- [ ] **Step 2: Add FP-11 to 防误判规则审查 table (after line 97, the FP-10 row)**

Add this row to the table:
```
| **FP-11** | **商品未物理出镜豁免（仅屏幕/截图/口头提及不算展示，有讲品但无实物展示不算 IPP）** |
```

- [ ] **Step 3: Verify changes**

Read the file to confirm the important reminders and FP table are correctly updated.

- [ ] **Step 4: Commit**

```bash
cd /Users/bytedance/Desktop/AIGC_IPP
git add prompts/chief_judge_system_prompt.txt
git commit -m "feat(prompts): add FP-11 to chief judge system prompt"
```

---

### Task 7: Update prompts/reviewer_user_prompt.txt

**Files:**
- Modify: `prompts/reviewer_user_prompt.txt:10` (重要提醒 section)
- Modify: `prompts/reviewer_user_prompt.txt:21` (常见误判场景提醒 section)
- Modify: `prompts/reviewer_user_prompt.txt:62` (防误判规则引用要求)

- [ ] **Step 1: Update 重要提醒 line 10**

Replace:
```
• **严格遵守防误判规则**（FP-01至FP-10），避免误伤
```

With:
```
• **严格遵守防误判规则**（FP-01至FP-11），避免误伤
```

- [ ] **Step 2: Add FP-11 to 常见误判场景提醒 (after line 21)**

After the line:
```
✓ **product_category 元数据与图片不一致不算（仅用于豁免判断，FP-10）**
```

Add:
```
✓ **有讲品但商品未物理出镜不算 IPP（FP-11）**：仅屏幕/截图/口头提及，无实物展示 → no_hit
```

- [ ] **Step 3: Update 防误判规则引用要求 line 62**

Replace:
```
4. 严格遵守防误判规则（FP-01至FP-10）
```

With:
```
4. 严格遵守防误判规则（FP-01至FP-11）
```

- [ ] **Step 4: Verify changes**

Read the file to confirm all three changes are correctly applied.

- [ ] **Step 5: Commit**

```bash
cd /Users/bytedance/Desktop/AIGC_IPP
git add prompts/reviewer_user_prompt.txt
git commit -m "feat(prompts): add FP-11 to reviewer user prompt"
```

---

### Task 8: Update prompts/chief_judge_user_prompt.txt

**Files:**
- Modify: `prompts/chief_judge_user_prompt.txt:5-7` (重要提醒 section)

- [ ] **Step 1: Update 重要提醒 lines 5-7**

Replace:
```
• **重点审查防误判规则（FP-01至FP-10）的应用情况**
• **特别关注 FP-08（纯颜色差异豁免）、FP-09（小物件/装饰品忽略）和 FP-10（product_category 仅用于豁免判断）的正确应用**
```

With:
```
• **重点审查防误判规则（FP-01至FP-11）的应用情况**
• **特别关注 FP-08（纯颜色差异豁免）、FP-09（小物件/装饰品忽略）、FP-10（product_category 仅用于豁免判断）和 FP-11（商品未物理出镜豁免）的正确应用**
```

- [ ] **Step 2: Verify changes**

Read the file to confirm the important reminders are correctly updated.

- [ ] **Step 3: Commit**

```bash
cd /Users/bytedance/Desktop/AIGC_IPP
git add prompts/chief_judge_user_prompt.txt
git commit -m "feat(prompts): add FP-11 to chief judge user prompt"
```

---

### Task 9: Push to GitHub

**Files:**
- Git push operation

- [ ] **Step 1: Check git status and log**

```bash
cd /Users/bytedance/Desktop/AIGC_IPP
git status
git log --oneline -10
```

Expected: All changes committed, clean working tree.

- [ ] **Step 2: Push to origin main**

```bash
cd /Users/bytedance/Desktop/AIGC_IPP
git push origin main
```

Expected: Push succeeds, all commits uploaded to GitHub.

- [ ] **Step 3: Verify push**

```bash
cd /Users/bytedance/Desktop/AIGC_IPP
git status
```

Expected: "Your branch is up to date with 'origin/main'."

---

## Self-Review Checklist

### 1. Spec Coverage
- [x] Version info updated → Task 1
- [x] Change log updated → Task 1
- [x] 判定流程 Step 2 updated → Task 2
- [x] FP-11 rule definition added → Task 3
- [x] 判定逻辑总结 table updated → Task 4
- [x] 判定示例 8 added → Task 4
- [x] reviewer_system_prompt.txt updated → Task 5
- [x] chief_judge_system_prompt.txt updated → Task 6
- [x] reviewer_user_prompt.txt updated → Task 7
- [x] chief_judge_user_prompt.txt updated → Task 8
- [x] Push to GitHub → Task 9

### 2. Placeholder Scan
- [x] No "TBD" or "TODO" in any task
- [x] All code blocks contain complete, exact content
- [x] All file paths are exact
- [x] All line numbers reference actual file locations

### 3. Consistency Check
- [x] FP-11 rule text is consistent across all files
- [x] "Product not physically shown exemption" used consistently as exemption_reason
- [x] FP numbering consistent (FP-11 follows FP-10)
- [x] Version number consistent (2026-06-23-v8)
