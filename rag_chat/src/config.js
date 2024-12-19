export const API_URL = process.env.VUE_APP_API_URL;
export const API_KEY = process.env.VUE_APP_API_KEY;
export const MODEL_NAME = process.env.VUE_APP_MODEL_NAME;
export const DOC_URL_TEMPLATE = process.env.VUE_APP_DOC_URL_TEMPLATE;
export const SERVER_NAME = process.env.VUE_APP_SERVER_NAME;
export const USER_NAME = process.env.VUE_APP_USER_NAME;
export const PROLOGUE = process.env.VUE_APP_PROLOGUE;
export const EXAMPLE_QUESTIONS = (() => {
  try {
    return process.env.VUE_APP_EXAMPLE_QUESTIONS
      ? JSON.parse(process.env.VUE_APP_EXAMPLE_QUESTIONS)
      : [];
  } catch (error) {
    console.error('解析 VUE_APP_EXAMPLE_QUESTIONS 失败:', error);
    return [];
  }
})();