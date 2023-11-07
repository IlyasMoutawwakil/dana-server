const crypto = require("crypto");

module.exports = {
  server: {
    ip: "localhost",
    port: 7000,
  },
  adminUser: [
    {
      username: process.env.ADMIN_USERNAME || "admin",
      password: process.env.ADMIN_PASSWORD || "admin",
      email: process.env.ADMIN_EMAIL || "admin@gmail.com",
    },
  ],
  secureCookie: false,
  apiToken: process.env.API_TOKEN || "api-token",
  sessionSecret: crypto.randomBytes(64).toString("hex"),
};
