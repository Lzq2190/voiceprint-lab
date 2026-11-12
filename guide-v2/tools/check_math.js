// 用本地 KaTeX 逐条渲染，找出所有语法错误。
// 用法: node check_math.js <json>
const fs = require("fs");
const path = require("path");
const katex = require(path.join(__dirname, "..", "assets", "katex", "katex.min.js"));

const file = process.argv[2];
const items = JSON.parse(fs.readFileSync(file, "utf8"));
let bad = 0;
items.forEach((it, i) => {
  try {
    katex.renderToString(it.tex, {
      displayMode: it.display,
      throwOnError: true,
      strict: false,
      trust: false,
      output: "html",
    });
  } catch (e) {
    bad++;
    console.log(`[ERR #${i + 1}] ${e.message.split("\n")[0]}`);
    console.log(`   TeX: ${it.tex.slice(0, 220).replace(/\n/g, " | ")}`);
  }
});
console.log(`渲染完成：${items.length - bad}/${items.length} 通过，${bad} 条失败`);
process.exit(bad ? 1 : 0);
