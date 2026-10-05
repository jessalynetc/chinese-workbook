# 产品需求文档 (PRD): 智能儿童中文启蒙图书生产系统
**Product OS Spec & Implementation Blueprint**
* 版本：v2.0 (Dual-Book System: Workbook & Color-by-Code)*  
* 适用平台：Amazon KDP (Print-on-Demand) + 网页扫码伴读 (Web Companion) + Google AI Studio (Gemini 1.5 Pro/Flash)*  
* 数据源：中华传统色开源库 ([nevertoday/zhongguo-traditional-colors](https://github.com/nevertoday/zhongguo-traditional-colors))*

---

## 1. 产品愿景与商业模型 (Product Vision & Business Model)

### 1.1 核心痛点与定位
* **目标客群**：海外华裔家庭、双语幼儿园、学龄前儿童（3–8 岁）家长。
* **市场痛点**：
  1. 市面现有中文识字本枯燥、机械描红重复率高，儿童易产生挫败感；
  2. 全彩儿童绘本在 Amazon KDP 印刷成本极高（120页全彩成本约 $8–$10），导致售价偏高缺乏竞争力；
  3. 传统填色画过于琐碎（如彩色玻璃马赛克风），不适合低幼儿童抓握蜡笔上色。
* **创新解法 (Hybrid Physical-Digital)**：
  * **纸质书**：采用 **黑白内页印刷**（极大降低 KDP 印刷成本至 $2.5–$3.2，可定出 $7.99–$9.99 的畅销定价）。
  * **数字化伴读 (Digital Companion)**：每页配备独立二维码，家长/儿童手机扫码秒开全彩参考图、标准普通话发音及中国传统色文化卡片。

---

## 2. 两个版本的产品矩阵 (Dual-Product Architecture)

### 2.1 产品 A: 《汉字大冒险》游戏化中文练习册 (Workbook)
* **规格**：US Letter (8.5 × 11 英寸), **128 页** (内页黑白)。
* **核心模式**：**以游戏代替死记硬背**。围绕 30 个核心汉字单元展开，每个汉字闭环包含 4 类互动游戏：
  1. **象形探秘 (Visual Metaphor)**：汉字演变全景，从甲骨文/象形图画到现代汉字；
  2. **汉字寻宝与迷宫 (Maze & Search)**：在由汉字笔画组成的图形迷宫中寻找目标汉字；
  3. **笔顺大闯关 (Trace & Grip)**：粗线条大号空心字笔画拆解描红；
  4. **字形辨析与连线 (Matching Game)**：形近字找茬、词义实物配对。
  5. **复习阶段卡**：每 5 个字设一次“汉字小勇士闯关棋盘”。

### 2.2 产品 B: 《中华传统色·汉字密码涂色书》 (Coloring Book)
* **规格**：US Letter (8.5 × 11 英寸), **80 页** (单面打印防透墨设计，40 张独立大画幅)。
* **视觉语言**：**Simple Chunky CBN v1.0**。
  * 每页仅包含 **25–45 个闭合大色块**；
  * 外轮廓 **4–5pt** 粗黑线条，内部分割线 **2.5–3pt**；
  * 色块中心清晰标注对应中文字符；
  * 顶部设计专用“蜡笔色卡图例（Crayon Legend）”。

---

## 3. 中国传统色彩与扫码交互系统 (Traditional Colors & Web Companion)

### 3.1 色彩标准库集成
接入 [nevertoday/zhongguo-traditional-colors](https://github.com/nevertoday/zhongguo-traditional-colors) 742 色库，精选 12 组高辨识度、适合儿童的传统色五色/六色方案：
* **五行大地色组**：朱红 (#E23E57)、魏紫 (#704276)、月白 (#D6ECF0)、荷叶绿 (#559B74)、琥珀黄 (#ECC058)。
* **节气天象色组**：青翠、黛蓝、秋葵黄、枣红、芙蓉红等。

### 3.2 纸电联动流程
1. **印刷版页面设计**：
   * 页面右上角保留 `1.2 × 1.2 cm` 的精细二维码；
   * 图例标明汉字与色名（如：`[日] = 080 琥珀黄`，`[木] = 490 荷叶绿`）。
2. **Web 伴读界面 (轻量静态 H5，托管于 GitHub Pages / Vercel)**：
   * 扫码进入：`https://chinese-colors.app/c/{page_id}`
   * 功能：
     - 展示该页 **100% 对应的矢量全彩完成图**；
     - 点击汉字播放标准发音；
     - 传统色文化小卡片（如“朱红源自丹砂，自古象征喜庆吉祥”）。

---

## 4. Google AI Studio 投产前文件清单与极速整理法

### 4.1 核心交付文件四件套
| 文件名 | 用途 | 格式 |
| :--- | :--- | :--- |
| `1. curriculum_100.json` | 100 核心字认知分级、拼音、英译、主题与传统色配比 | JSON |
| `2. system_instruction_cbn.md` | AI Studio 注入的系统级填色构图与几何硬性约束 | Markdown |
| `3. system_instruction_wb.md` | AI Studio 注入的游戏练习题（迷宫、连线、拼图）生成规则 | Markdown |
| `4. response_schema.json` | 强类型输出验证规范，确保 API 返回纯粹的 SVG 与元数据 | JSON Schema |

---

## 5. 汉字象形图画自动生成 Skill (Pictographic Character-to-Artwork) 实施蓝图

### 5.1 核心难点与解法
* 痛点：通用图像模型（如 Midjourney）无法精准捕捉汉字本身的骨架，只会画泛泛的实物。
* 解决方案：**骨架感知 + 语义隐喻（Skeleton-Aware Metaphor Pipeline）**。
  1. **第 1 层：骨架锚定 (Glyph Skeleton)**：读取汉字标准楷体 SVG 骨架路径；
  2. **第 2 层：Gemini 多模态形义映射**：Gemini 1.5 Pro 分析字形特征（如“雨”字：上横为云，框中竖挑为雨线，四点为水滴）；
  3. **第 3 层：粗描边矢量重构 (Chunky Vectorization)**：以字形为骨架，扩充为圆润闭合大色块。

### 5.2 平台选型推荐
* **推荐方案：Google AI Studio API + 本地 Python 后处理**
  * 理由：Gemini 1.5 Pro 原生具备中文深度理解、长上下文少样本学习（Few-shot）以及输出高质量 SVG 代码的能力。
  * 流程：通过 AI Studio 设计调校 Prompt，本地脚本批量调取并做字体转曲与尺寸合规检查。
