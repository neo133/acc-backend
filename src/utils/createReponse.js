export const sendHttpResponse = (res, message, data = {}, statusCode = 200, success = true) =>
  res.status(statusCode).json({
    success,
    message,
    data
  });
