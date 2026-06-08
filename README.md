# AIGC_IPP

AIGC 挂车商品与讲解商品不一致（货不对板）检测规则仓库

AIGC Inconsistent Product Presentation (IPP) Detection Rules

**当前规则版本**: 2026-06-08-v5

## 文件结构

```
AIGC_IPP/
├── rules/
│   └── rules_text.txt              # 规则文件（Aicolate通过raw URL获取）
├── prompts/
│   ├── reviewer_system_prompt.txt    # 专家评审系统提示词
│   ├── reviewer_user_prompt.txt      # 专家评审用户提示词
│   ├── chief_judge_system_prompt.txt # 首席裁判系统提示词
│   └── chief_judge_user_prompt.txt   # 首席裁判用户提示词
├── analyze_csv.py                  # 解析Aicolate批量运行结果
├── generate_excel.py               # 生成人工审核Excel文档
├── generate_review_doc.py          # 生成人工审核Markdown文档
└── README.md
```

## 规则文件

- `rules/rules_text.txt` - 货不对板检测规则（适用于 EU 地区所有内容，AIGC + 非AIGC）

## 规则说明

| 编号 | 规则名称 | 说明 |
|------|---------|------|
| IPP01 | 货不对板 | 视频中展示的商品与挂车商品主图不一致 |

## 规则文件 URL

```
https://raw.githubusercontent.com/danielwanyan/AIGC_IPP/main/rules/rules_text.txt
```

## 判定逻辑

有商品推广 + 视频帧商品与挂车商品不一致 → 命中（除非豁免）

**重要说明**：所有内容都需要分析，`aigc_video_id` 仅用于区分问题类型（AIGC_IPP / non-AIGC_IPP），不是跳过条件。

### 豁免规则

1. **盲盒/首饰/玉石/卡牌**：同三级类目 → 豁免
2. **服饰（上下装）**：同SPU不同SKU（仅颜色/花纹差异）→ 豁免
3. **全类目纯颜色差异**：功能款式结构完全一致，仅颜色不同 → 豁免（FP-08）

### 防误判规则（FP-01 至 FP-09）

| 规则 | 说明 |
|------|------|
| FP-01 | 光线/色差差异不算不一致 |
| FP-02 | 品牌名称/OCR文字不对比 |
| FP-03 | 设计效果图 vs 实物差异不算 |
| FP-04 | 仅基于给定图片对比，不假设其他变体 |
| FP-05 | 服饰穿着方式差异不算 |
| FP-06 | 多商品场景：只要挂车商品出现且一致就不命中 |
| FP-07 | 包装文字语言差异不算 |
| **FP-08** | **纯颜色差异豁免（功能款式结构一致，全类目适用）** |
| **FP-09** | **小物件/装饰品忽略（只对比商品本身）** |

### 判定流程

```
Step 1: 检查是否有商品推广（ASR/OCR）
    ├─ 无推广 → 不命中
    └─ 有推广 → 进入商品对比

Step 2: 商品对比（视频帧商品 vs 挂车商品主图）
    ├─ 一致 → 不命中
    └─ 不一致 → 进入豁免检查

Step 3: 豁免检查
    ├─ 盲盒/首饰/玉石/卡牌 + 同三级类目 → 豁免
    ├─ 服饰 + 同SPU不同SKU → 豁免
    ├─ 全类目 + 仅颜色不同（功能款式结构一致）→ 豁免（FP-08）
    └─ 其他 → 命中
```

## 系统架构（3+1 陪审团模式）

```
输入 → 3位专家并行评审 → 首席裁判汇总 → 最终裁决
```

- **专家1**: Gemini3-Pro
- **专家2**: GPT5.4
- **专家3**: GPT5.1
- **首席裁判**: 汇总3位专家意见，重点审查防误判规则应用
