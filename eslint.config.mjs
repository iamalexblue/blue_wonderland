import antfu from '@antfu/eslint-config'

export default antfu({
  formatters: true,
  unocss: true,
  astro: true,
}, {
  rules: {
    // 统一 brace 风格为 1tbs，与 prettier 默认一致（antfu 默认 stroustrup 与旧版 prettier 冲突）
    'style/brace-style': ['error', '1tbs'],
  },
})
