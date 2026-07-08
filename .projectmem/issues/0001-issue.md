# #0001 微信支付成功的订单仍可被用户取消并硬删除，导致商户已收款但后台订单记录消失

- 2026-07-05T05:14:47Z `issue`: 微信支付成功的订单仍可被用户取消并硬删除，导致商户已收款但后台订单记录消失 [flour-mill-miniapp server src/routes/orders.js]
- 2026-07-05T05:29:08Z `attempt`: Added payment audit fields, blocked cancel/delete for paid WeChat orders, restored deleted paid order 12, and refreshed auth roles from DB; health and syntax checks passed [server src/routes/orders.js, src/db.js, src/middleware/auth.js; miniapp pages/orderlist/orderlist.js, pages/orderdetail/orderdetail.js] (worked)
- 2026-07-05T05:29:12Z `fix`: Confirmed WeChat-paid orders are now preserved with transaction_id/paid_at, cannot be user-cancelled or deleted, and recovered order FM20260705TTHUTW is visible again [flour-mill payment/order backend and orderlist/orderdetail UI]
