# projectmem - Obsidian

_Last updated: 2026-07-05_

## Project purpose
This repository is the shared Obsidian AI memory vault at `C:\Users\NINGMEI\Documents\Obsidian` on Windows. It mirrors the Mac mini vault at `/Users/xiaosong/Documents/Obsidian Vault` and stores human-readable project notes, agent configuration notes, templates, and the projectmem active-memory database used by coding agents. The vault helps Codex, OpenClaw, Claude, Cursor, OpenCode, and related tools share durable context without storing secrets in notes.

## Recent issues
- [DONE] #0010 Order list/detail show raw refund status such as refunded and raw ISO timestamps instead of customer-friendly Chinese labels and local time. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\pages\orderlist\orderlist.js] -> Order list/detail now show refunded/refunding/refund_failed as Chinese status labels and display readable local timestamps; verified with node --check. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\pages\orderlist\orderlist.js] (fixed)
- [DONE] #0009 Public product endpoints read req.user.price_tier without auth middleware, so wholesale users see retail prices in product listings/details. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\products.js] -> Product list/detail routes now use optional auth so token-bearing wholesale users can receive wholesale showing_price while guests still see retail; syntax check passed. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\products.js] (fixed)
- [DONE] #0008 Admin credit page displays credit_available, but backend /admin/credit returns credit_remaining, so available credit can render blank. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\pages\admin\admin.wxml] -> Admin credit API now returns credit_available as an alias of credit_remaining, matching the miniapp admin credit page binding; syntax check passed. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\admin.js] (fixed)
- [DONE] #0007 Admin user role buttons send role changes, but PUT /admin/users/:id only accepts price_tier and credit_limit, so role changes do not persist. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\admin.js] -> Admin role updates now persist because PUT /admin/users/:id includes role in the update whitelist; admin route syntax check passed. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\admin.js] (fixed)
- [DONE] #0006 Backend cannot run locally because node_modules is absent and auth.js requires uuid, which is not declared in package.json dependencies. [C:\Users\NINGMEI\flour-mill-miniapp\backend\package.json] -> Removed undeclared uuid dependency by using Node crypto.randomUUID, installed backend npm dependencies, and verified backend routes can be required without missing-module errors. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\auth.js] (fixed)
- [DONE] #0005 Miniapp is currently hardwired to USE_MOCK=true, so it uses local fake data and does not call the real xinjiangyuwen.cn backend. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\utils\api.js] -> Set USE_MOCK=false and verified utils/api.js syntax so the miniapp calls the real https://xinjiangyuwen.cn/api backend instead of local mock data. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\utils\api.js] (fixed)
- [OPEN] #0004 Miniapp workspace contains an empty .git directory; git status fails with 'not a git repository'. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\.git] (open)
- [DONE] #0003 Miniapp frontend has USE_MOCK=true, so it uses local mock data instead of production API/payment endpoints. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\utils\api.js:2] -> USE_MOCK is now false, so production API/payment endpoints are used instead of local mock data; utils/api.js syntax check passed. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\utils\api.js] (fixed)
- [DONE] #0002 Miniapp admin page requests /admin/products but backend lacks GET /admin/products and admin category listing endpoints, so real admin product management cannot load data. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\products.js] -> Added admin category/product listing endpoints required by the miniapp admin page and verified products route syntax after the fixes. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\products.js] (fixed)
  - Partial attempt: Added GET /admin/products and GET /admin/categories, plus safer category deletion checks; verification still pending. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\products.js]
  - Partial attempt: Adjusted category deletion guard to count all products, including inactive ones, so MySQL foreign-key deletes do not fail unexpectedly; final verification pending. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\products.js]
- [DONE] #0001 微信支付成功的订单仍可被用户取消并硬删除，导致商户已收款但后台订单记录消失 [flour-mill-miniapp server src/routes/orders.js] -> Confirmed WeChat-paid orders are now preserved with transaction_id/paid_at, cannot be user-cancelled or deleted, and recovered order FM20260705TTHUTW is visible again [flour-mill payment/order backend and orderlist/orderdetail UI] (fixed)

## Decisions
- Use /Users/xiaosong/Documents/Obsidian as the shared AI memory vault for agents, with Obsidian notes for human-readable project records and projectmem for append-only active development memory. [/Users/xiaosong/Documents/Obsidian]
- Configure supported agents through MCP servers named obsidian and projectmem so Codex, Claude, OpenCode, Cursor, and OpenClaw can share the same vault and memory workflow. [/Users/xiaosong/Documents/Obsidian/Agent-Configs/MCP 配置总览.md]
- Add the Spring Kangli flour group QR code as a customer-service entry on the miniapp Profile page so customers can preview or long-press the group code from the My tab. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\pages\profile\profile.wxml]
- Admin refunds use WeChat Pay V3 full-order refund only: POST /api/admin/orders/:id/refund creates a refund, records refund_out_no/refund_id/status, and refund callbacks move orders to refunded/refund_failed. [flour-mill-miniapp payment/refund flow]
- Use a lightweight in-miniapp admin order reminder: when an admin opens the Profile tab, check pending admin orders, show a tab/menu badge, vibrate, and offer to open the admin backend. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\pages\profile\profile.js]
- Use 15276091001 as the Xinjiang Yuwen admin/customer-service WeChat phone in miniapp contact surfaces; admin access remains controlled by WeChat login openid plus backend role=admin. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\utils\promo.js]

## Notes
- gotcha: The conversation cwd /Users/xiaosong/Documents/openclow 2 is currently a 0-byte file, not a directory; use /Users/xiaosong/Documents/Obsidian for the vault and ~/.openclaw for OpenClaw config. [/Users/xiaosong/Documents/openclow 2]
- Installed Obsidian desktop app 1.12.7 to /Applications and opened the shared vault path /Users/xiaosong/Documents/Obsidian.
- Project map initialized for the Obsidian AI memory vault, including purpose, main folders, entry points, and suggested first reads. [/Users/xiaosong/Documents/Obsidian/.projectmem/PROJECT_MAP.md]
- Created visible Obsidian project folders for OpenClaw and Codex under 01-Projects, and initialized projectmem in both real project paths.
- Synchronized the AI memory vault content into the Obsidian app's active vault at /Users/xiaosong/Documents/Obsidian Vault, updated Codex/OpenClaw MCP targets to that visible vault, and kept tool runtimes under /Users/xiaosong/Documents/Obsidian.
- Mirrored the Mac mini Obsidian Vault into the Windows vault at C:\Users\NINGMEI\Documents\Obsidian, copied MCPVault/projectmem integration sources, installed a Windows .venv-projectmem, and added Windows MCP configuration snippets plus Scripts/connect-project-memory.ps1.
- gotcha: Codex bundled/remote plugin display names can be localized by editing cached plugin.json interface fields, but cache updates may overwrite them; internal plugin name IDs must remain normalized English. [C:\Users\NINGMEI\.codex\plugins\cache]
- Created Obsidian project note for Codex plugin localization at 01-Projects/Codex/Codex 插件中文化项目.md and linked it from Codex README plus 01-Projects/项目索引.md. [01-Projects/Codex/Codex 插件中文化项目.md]
- gotcha: The Spring Kangli WeChat group QR image says it is valid for 7 days until before 2026-07-12, so the packaged asset must be replaced when the group QR expires. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\images\groups\chun-kang-li-group.jpg]
- gotcha: In this Codex session, projectmem summary/map resolve to the Obsidian vault, while the active cwd is the flour-mill miniapp; verify local files before acting on miniapp structure. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp]

## Key files
- `/.openclaw`
- `1.12.7`
- `Scripts/connect-project-memory.ps1`
- `plugin.json`
- `插件中文化项目.md`
- `01-Projects/项目索引.md`
- `xinjiangyuwen.cn`
- `auth.js`
- `package.json`
- `req.user.price`
- `utils/api.js`
- `//xinjiangyuwen.cn`
- `crypto.randomUUID`

## Open questions
- None logged yet.
