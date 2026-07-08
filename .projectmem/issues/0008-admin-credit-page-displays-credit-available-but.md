# #0008 Admin credit page displays credit_available, but backend /admin/credit returns credit_remaining, so available credit can render blank.

- 2026-07-05T09:51:44Z `issue`: Admin credit page displays credit_available, but backend /admin/credit returns credit_remaining, so available credit can render blank. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\pages\admin\admin.wxml]
- 2026-07-05T09:58:08Z `fix`: Admin credit API now returns credit_available as an alias of credit_remaining, matching the miniapp admin credit page binding; syntax check passed. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\admin.js]
