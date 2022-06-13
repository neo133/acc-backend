const prettierOptions = require('./.prettierrc');

module.exports = {
  root: true,
  env: {
    browser: true,
    commonjs: true,
    es2021: true,
    node: true
  },
  extends: ['airbnb-base', 'prettier', 'prettier/prettier'],
  plugins: ['prettier'],
  parserOptions: {
    ecmaVersion: 12
  },
  rules: {
    camelcase: 'off',
    'prettier/prettier': ['error', prettierOptions],
    'import/no-extraneous-dependencies': 0,
    'import/prefer-default-export': 0,
    'no-param-reassign': 0,
    'no-nested-ternary': 0,
    'no-underscore-dangle': 0,
    'no-plusplus': 0,
    'max-classes-per-file': 0,
    'import/no-cycle': 0,
    'jsx-a11y/click-events-have-key-event': 0,
    'import/no-named-as-default': 0,
    'no-return-await': 0,
    'no-console': 0
  }
};
