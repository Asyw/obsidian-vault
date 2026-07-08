# #0010 Order list/detail show raw refund status such as refunded and raw ISO timestamps instead of customer-friendly Chinese labels and local time.

- 2026-07-05T10:04:49Z `issue`: Order list/detail show raw refund status such as refunded and raw ISO timestamps instead of customer-friendly Chinese labels and local time. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\pages\orderlist\orderlist.js]
- 2026-07-05T10:06:04Z `attempt`: Mapped refund statuses to Chinese labels and formatted created_at into YYYY-MM-DD HH:mm on order list/detail pages; JS syntax checks passed. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\pages\orderlist\orderlist.js] (worked)
- 2026-07-05T10:06:11Z `fix`: Order list/detail now show refunded/refunding/refund_failed as Chinese status labels and display readable local timestamps; verified with node --check. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\pages\orderlist\orderlist.js]
