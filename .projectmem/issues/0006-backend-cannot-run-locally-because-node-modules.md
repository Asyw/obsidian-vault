# #0006 Backend cannot run locally because node_modules is absent and auth.js requires uuid, which is not declared in package.json dependencies.

- 2026-07-05T09:51:34Z `issue`: Backend cannot run locally because node_modules is absent and auth.js requires uuid, which is not declared in package.json dependencies. [C:\Users\NINGMEI\flour-mill-miniapp\backend\package.json]
- 2026-07-05T09:57:54Z `fix`: Removed undeclared uuid dependency by using Node crypto.randomUUID, installed backend npm dependencies, and verified backend routes can be required without missing-module errors. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\auth.js]
