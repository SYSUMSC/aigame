FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/node:24.14.0-bookworm AS builder

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build && node <<'NODE'
const fs = require('fs');
const p = '.output/server/chunks/build/server.mjs';

if (fs.existsSync(p)) {
  const s = fs.readFileSync(p, 'utf8');
  const marker = "import require$$0, {";
  const suffix = "} from 'vue';";
  const i = s.indexOf(marker);
  const j = i >= 0 ? s.indexOf(suffix, i) : -1;
  if (i >= 0 && j > i) {
    const names = s.slice(i + marker.length, j).trim();
    const replacement =
      "import * as require$$0 from 'vue';\n" +
      "import { " + names + " } from 'vue';";
    fs.writeFileSync(p, s.slice(0, i) + replacement + s.slice(j + suffix.length), 'utf8');
    console.log('patched vue import for node24 compatibility');
  }
}
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
