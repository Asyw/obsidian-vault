# #0009 Public product endpoints read req.user.price_tier without auth middleware, so wholesale users see retail prices in product listings/details.

- 2026-07-05T09:51:48Z `issue`: Public product endpoints read req.user.price_tier without auth middleware, so wholesale users see retail prices in product listings/details. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\products.js]
- 2026-07-05T09:58:12Z `fix`: Product list/detail routes now use optional auth so token-bearing wholesale users can receive wholesale showing_price while guests still see retail; syntax check passed. [C:\Users\NINGMEI\flour-mill-miniapp\backend\src\routes\products.js]
