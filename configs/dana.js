module.exports = {
  server: {
    ip: "localhost",
    port: 7000,
  },
  adminUser: [
    {
      username: "admin",
      password: "admin",
      email: "admin@gmail.com",
    },
  ],
  secureCookie: false,
  sessionSecret: "secret",
  apiToken: "secret",
};
