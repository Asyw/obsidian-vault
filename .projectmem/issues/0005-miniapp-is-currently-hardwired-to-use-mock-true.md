# #0005 Miniapp is currently hardwired to USE_MOCK=true, so it uses local fake data and does not call the real xinjiangyuwen.cn backend.

- 2026-07-05T09:51:31Z `issue`: Miniapp is currently hardwired to USE_MOCK=true, so it uses local fake data and does not call the real xinjiangyuwen.cn backend. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\utils\api.js]
- 2026-07-05T09:57:49Z `fix`: Set USE_MOCK=false and verified utils/api.js syntax so the miniapp calls the real https://xinjiangyuwen.cn/api backend instead of local mock data. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\utils\api.js]
