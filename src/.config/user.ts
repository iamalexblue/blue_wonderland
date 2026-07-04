import type { UserConfig } from '~/types'

export const userConfig: Partial<UserConfig> = {
  // Override the default config here
  // site: { title: "講評世界" },
  // seo: { twitter: "@moeyua13" },
  appearance: {
    fonts: {
      header:
        '"LXGW WenKai GB", "霞鹜文楷", "Source Han Serif SC", "Source Han Serif CN", serif',
      ui: '"LXGW WenKai GB", "霞鹜文楷", "Source Han Sans SC", "PingFang SC", "PingFang HK", sans-serif',
    },
  },
}
