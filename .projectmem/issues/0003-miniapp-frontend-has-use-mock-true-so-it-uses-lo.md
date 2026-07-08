# #0003 Miniapp frontend has USE_MOCK=true, so it uses local mock data instead of production API/payment endpoints.

- 2026-07-05T09:51:11Z `issue`: Miniapp frontend has USE_MOCK=true, so it uses local mock data instead of production API/payment endpoints. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\utils\api.js:2]
- 2026-07-05T09:58:19Z `fix`: USE_MOCK is now false, so production API/payment endpoints are used instead of local mock data; utils/api.js syntax check passed. [D:\微信小程序开发\面粉厂小程序\flour-mill-miniapp\utils\api.js]
