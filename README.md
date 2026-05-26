# AIGC_IPP

AIGC 挂车商品与讲解商品不一致（货不对板）检测规则仓库

AIGC Inconsistent Product Presentation (IPP) Detection Rules

## 规则文件

- `rules/rules_text.txt` - AIGC货不对板检测规则

## 规则说明

| 编号 | 规则名称 | 说明 |
|------|---------|------|
| IPP01 | AIGC货不对板 | AIGC视频中展示的商品与挂车商品主图不一致 |

## 规则文件 URL

```
https://raw.githubusercontent.com/danielwanyan/AIGC_IPP/main/rules/rules_text.txt
```

## 判定逻辑

AIGC视频 + 有商品推广 + 视频帧商品与挂车商品不一致 → 命中（除非豁免）

### 豁免规则

1. **盲盒/首饰/玉石/卡牌**：同三级类目 → 豁免
2. **服饰（上下装）**：同SPU不同SKU（仅颜色/花纹差异）→ 豁免

### 判定流程

```
Step 1: 检查 is_aigc 字段
    ├─ null → 跳过
    └─ 有值 → 进入分析

Step 2: 检查是否有商品推广（ASR/OCR）
    ├─ 无推广 → 不命中
    └─ 有推广 → 进入商品对比

Step 3: 商品对比（视频帧商品 vs 挂车商品主图）
    ├─ 一致 → 不命中
    └─ 不一致 → 进入豁免检查

Step 4: 豁免检查
    ├─ 盲盒/首饰/玉石/卡牌 + 同三级类目 → 豁免
    ├─ 服饰 + 同SPU不同SKU → 豁免
    └─ 其他 → 命中
```
