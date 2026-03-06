FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/node:24.14.0-bookworm AS builder

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

# 先仅拷贝 Prisma schema，并显式生成 Prisma Client。
# 这样可以和构建缓存解耦，也能确保 Nitro 产物引用的运行时文件稳定存在。
COPY prisma ./prisma
RUN pnpm prisma:generate

COPY . .
RUN pnpm build && node <<'NODE'
const fs = require('fs');

function patchFile(filePath, replacer) {
  if (!fs.existsSync(filePath)) {
    return;
  }

  const source = fs.readFileSync(filePath, 'utf8');
  const next = replacer(source);
  if (next !== source) {
    fs.writeFileSync(filePath, next, 'utf8');
    console.log(`patched compatibility imports in ${filePath}`);
  }
}

patchFile('.output/server/chunks/build/server.mjs', (source) => {
  const marker = "import require$$0, {";
  const suffix = "} from 'vue';";
  const start = source.indexOf(marker);
  const end = start >= 0 ? source.indexOf(suffix, start) : -1;

  if (start < 0 || end <= start) {
    return source;
  }

  const names = source.slice(start + marker.length, end).trim();
  const replacement =
    "import * as require$$0 from 'vue';\n" +
    `import { ${names} } from 'vue';`;
  return source.slice(0, start) + replacement + source.slice(end + suffix.length);
});

patchFile('.output/server/chunks/nitro/nitro.mjs', (source) => {
  const target = "import { PrismaClient } from '@prisma/client';";
  if (!source.includes(target)) {
    return source;
  }

  return source.replace(
    target,
    "import prismaPkg from '@prisma/client';\nconst { PrismaClient } = prismaPkg;",
  );
});
NODE

FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/node:24.14.0-bookworm AS runner

WORKDIR /app

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000 \
    NUXT_PORT=3000

COPY --from=builder /app/.output /app/.output
COPY --from=builder /app/node_modules /app/node_modules
COPY --from=builder /app/package.json /app/package.json

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
