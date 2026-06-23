# FP-11 商品未物理出镜豁免规则设计文档

**日期**: 2026-06-23
**版本**: v1.0
**状态**: 待审核

## 1. 背景与目的

### 1.1 问题描述
在当前 IPP（货不对板）检测流程中，存在以下误判场景：
- ASR/OCR 有明确的商品推广内容
- 但视频帧中挂车商品仅出现在手机屏幕、电脑截图中，或仅口头提及
- 商品本身没有以实物形式物理出镜
- 现有规则会将此类场景判定为"类目不一致"而命中

### 1.2 业务影响
- **误伤案例**：parsed_results.json 中 row_num 16、row_num 36 等案例
- **典型场景**：主播口头讲解商品 + 屏幕展示商品图片，但实物未出镜
- **核心问题**：没有物理实物可供对比，无法判断是否"货不对板"

### 1.3 设计目标
新增防误判规则 FP-11，明确"有讲品但商品未物理出镜不算 IPP"，降低此类误伤。

## 2. 规则定义

### 2.1 FP-11 规则内容

**规则名称**：商品未物理出镜豁免
**规则编号**：FP-11

**判定规则**：
- 如果 ASR/OCR 有商品推广，但视频帧中**未出现挂车商品的物理实物展示** → **豁免（no_hit）**
- 物理实物展示定义：商品以真实实物形式出现在视频中（手持、摆放、穿戴等）
- 以下情况**不属于**物理实物展示：
  - 商品仅出现在手机屏幕、电脑屏幕、电视屏幕等电子屏幕中
  - 商品仅出现在截图、图片展示中
  - 仅口头提及商品，没有任何视觉展示

**例外情况**：
- 如果视频帧中出现了**其他商品的物理展示**（与挂车商品不同类型）→ 仍需判断是否不一致（不适用 FP-11）
- 例如：推广咖啡机但视频展示搅拌机 → 仍判定为 hit（类目不一致）

### 2.2 判定流程更新

在 Step 2 商品对比中新增物理出镜检查：

```
Step 2: 商品对比（视频帧商品 vs 挂车商品全量图片）
    ├─ 首先检查：视频帧中是否有挂车商品的物理实物展示？
    │   ├─ 无物理展示（仅屏幕/截图/口头）→ 不命中（no_hit，FP-11）
    │   └─ 有物理展示 → 继续对比
    ├─ 视频帧商品与任意一张商品图片一致 → 不命中（no_hit）
    └─ 视频帧商品与所有商品图片都不一致 → Step 3
```

### 2.3 判定逻辑总结新增

| 情况 | 结果 | 说明 |
|------|------|------|
| 有推广 + 商品未物理出镜（仅屏幕/截图/口头） | no_hit | 商品未物理展示，无法对比（FP-11） |

## 3. 受影响文件

### 3.1 规则文档
- **文件**: `rules/rules_text.txt`
- **更新内容**:
  1. 版本信息更新为 2026-06-23-v8
  2. 判定流程 Step 2 更新
  3. 新增 FP-11 规则详细说明（在 FP-10 之后）
  4. 判定逻辑总结表新增一行
  5. 新增判定示例 8（FP-11 示例）
  6. 变更日志新增 v8 记录

### 3.2 专家评审系统提示词
- **文件**: `prompts/reviewer_system_prompt.txt`
- **更新内容**:
  1. 核心原则部分新增"5.1 商品物理出镜检查"
  2. 防误判原则部分新增 FP-11 说明
  3. 防误判规则列表新增 FP-11

### 3.3 首席裁判系统提示词
- **文件**: `prompts/chief_judge_system_prompt.txt`
- **更新内容**:
  1. 重要提醒部分更新为 FP-01 至 FP-11
  2. 特别关注列表新增 FP-11
  3. 防误判规则审查表格新增 FP-11

### 3.4 专家评审用户提示词
- **文件**: `prompts/reviewer_user_prompt.txt`
- **更新内容**:
  1. 重要提醒部分更新为 FP-01 至 FP-11
  2. 常见误判场景提醒新增 FP-11
  3. 防误判规则引用要求更新为 FP-01 至 FP-11

### 3.5 首席裁判用户提示词
- **文件**: `prompts/chief_judge_user_prompt.txt`
- **更新内容**:
  1. 重要提醒部分更新为 FP-01 至 FP-11
  2. 特别关注列表新增 FP-11

## 4. 示例

### 4.1 FP-11 适用场景（no_hit）

**输入**:
- ASR: "Buy this lymphatic drainage supplement! Only $29.99!"
- 视频帧：医疗解剖动画 + 穿白大褂的人讲解
- 挂车商品图片：瓶装补充剂
- 检查：视频帧中无补充剂实物展示

**输出**:
```json
{
  "decision": "no_hit",
  "issue_type": "AIGC_IPP",
  "inconsistency_type": null,
  "exemption_check": {
    "category_type": "normal",
    "is_exempted": true,
    "exemption_reason": "Product not physically shown exemption"
  },
  "reason": "Product is promoted in ASR but not physically shown in any video frames (only AIGC-generated medical imagery). Cannot determine if product is consistent or not. FP-11 applies.",
  "frames_analyzed": [1, 2, 3, 4, 5],
  "frames_with_product": []
}
```

### 4.2 FP-11 不适用场景（仍 hit）

**输入**:
- ASR: "Buy this coffee machine!"
- 视频帧：展示一台搅拌机（物理实物）
- 挂车商品图片：咖啡机
- 检查：视频中有物理实物展示，但是错误的商品

**输出**:
```json
{
  "decision": "hit",
  "issue_type": "AIGC_IPP",
  "inconsistency_type": "category",
  "exemption_check": {
    "category_type": "normal",
    "is_exempted": false,
    "exemption_reason": null
  },
  "reason": "Video shows a blender (physically present) but bound product is a coffee machine - completely different product categories. FP-11 does not apply because a different product is physically shown.",
  "frames_analyzed": [1, 2, 3, 4, 5],
  "frames_with_product": [1, 2, 3, 4, 5]
}
```

## 5. 首席裁判审查要点

### 5.1 FP-11 应用检查
- 专家是否正确识别了"商品未物理出镜"的场景？
- 专家是否正确区分了"物理实物展示"和"屏幕/截图展示"？
- 专家是否错误地将"有其他商品物理展示"的场景应用了 FP-11？

### 5.2 输出字段检查
- `fp_rules_applied` 应包含 "FP-11"（如果适用）
- `exemption_reason` 应为 "Product not physically shown exemption"
- `frames_with_product` 应为空数组（如果未物理出镜）

## 6. 风险与注意事项

### 6.1 潜在风险
- **漏判风险**：如果视频中确实有商品物理展示但专家未识别到，可能导致漏判
- **边界模糊**：某些场景可能难以区分"实物展示"和"屏幕展示"（如商品图片打印出来手持）

### 6.2 缓解措施
- 在判定流程中明确要求"详细对比验证是否商品真的没出镜"
- 要求专家在 reason 中明确说明哪些帧有/没有商品展示
- 首席裁判重点审查 FP-11 的应用情况

## 7. 验收标准

- [ ] 规则文档已更新，包含 FP-11 完整说明
- [ ] 所有 prompt 文件已更新，包含 FP-11 提醒
- [ ] parsed_results.json 中 row_num 16、row_num 36 等案例重新判定后应为 no_hit
- [ ] 专家输出中正确引用 FP-11 规则编号
- [ ] 首席裁判输出中正确审查 FP-11 应用情况
