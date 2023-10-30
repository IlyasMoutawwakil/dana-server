const crypto = require("crypto");

module.exports = {
  server: {
    ip: "localhost",
    port: 7000,
  },
  adminUser: [
    {
      username: "admin",
      password: process.env.ADMIN_PASSWORD || "admin",
      email: process.env.ADMIN_EMAIL || "admin@gmail.com",
    },
    {
      username: "amd-user",
      password: process.env.AMD_USER_PASSWORD || "amd-user",
      email: process.env.AMD_USER_EMAIL || "amd-user@gmail.com",
    },
    {
      username: "nvidia-user",
      password: process.env.NVIDIA_USER_PASSWORD || "nvidia-user",
      email: process.env.NVIDIA_USER_EMAIL || "nvidia-user@gmail.com",
    },
  ],
  secureCookie: false,
  apiToken: process.env.API_TOKEN,
  sessionSecret: crypto.randomBytes(64).toString("hex"),
};
