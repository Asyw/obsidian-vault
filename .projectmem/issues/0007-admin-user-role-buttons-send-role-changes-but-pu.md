# #0007 Admin user role buttons send role changes, but PUT /admin/users/:id only accepts price_tier and credit_limit, so role changes do not persist.

- 2026-07-05T09:51:41Z `issue`: Admin user role buttons send role changes, but PUT /admin/users/:id only accepts price_tier and credit_limit, so role changes do not persist. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\admin.js]
- 2026-07-05T09:57:59Z `attempt`: Updated PUT /admin/users/:id to accept role in addition to price_tier and credit_limit; route syntax check passed. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\admin.js] (worked)
- 2026-07-05T09:58:03Z `fix`: Admin role updates now persist because PUT /admin/users/:id includes role in the update whitelist; admin route syntax check passed. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\admin.js]
