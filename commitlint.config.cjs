const gitmojiParserOpts = require('@gitmoji/parser-opts');
const gitmojiPlugin = require('commitlint-plugin-gitmoji');

/** @type {import('@commitlint/types').UserConfig} */
module.exports = {
  extends: ['@commitlint/config-conventional'],
  parserPreset: {
    parserOpts: gitmojiParserOpts,
    plugins: {
      gitmoji: gitmojiPlugin,
    },
  },
  plugins: [gitmojiPlugin],
  rules: {
    'start-with-gitmoji': [2, 'always'],
    'type-enum': [
      2,
      'always',
      [
        'feat',
        'fix',
        'docs',
        'style',
        'refactor',
        'perf',
        'test',
        'chore',
        'build',
        'ci',
        'a11y',
        'security',
        'revert',
      ],
    ],
    'scope-case': [2, 'always', 'lower-case'],
    'subject-case': [2, 'always', 'sentence-case'],
    'subject-empty': [2, 'never'],
    'type-empty': [2, 'never'],
    'header-max-length': [2, 'always', 100],
    'body-leading-blank': [2, 'always'],
    'footer-leading-blank': [2, 'always'],
    'subject-full-stop': [2, 'never', '.'],
    'type-case': [2, 'always', 'lower-case'],
  },
};
